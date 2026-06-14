"""Deterministic Daily Intelligence Brief generation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from radar.json_utils import read_json, write_json


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRIDGE_ROOT = Path(
    r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"
)
DEFAULT_PROJECT_IMPACT_MAP_PATH = REPO_ROOT / "config" / "project_impact_map.json"
DAILY_BRIEFS_DIRNAME = "daily_briefs"
DAILY_SIM_DIR_PREFIX = "0320_0400_daily_sim_"
FORBIDDEN_PREFIXES = ("LAST-", "latest-")
FORBIDDEN_ACTIONS = (
    "runtime_llm_call",
    "auto_action",
    "email_or_notification",
    "scheduler_mutation",
    "hag_bypass",
    "bypass_403",
    "external_command_execution",
)


def build_daily_intelligence(
    run_dir: str | Path,
    *,
    project_map_path: str | Path = DEFAULT_PROJECT_IMPACT_MAP_PATH,
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    """Build Human Daily Brief, AI Model Packet and impact map from one run."""
    root = Path(run_dir).expanduser().resolve()
    if _has_forbidden_path_part(root):
        raise ValueError("run_dir must not use LAST-* or latest-* names.")
    data = _load_run_data(root)
    project_map = load_project_impact_map(project_map_path)
    generated_at = generated_at_utc or _utc_now()
    run_id = root.name
    brief_date = _date_from_run_id(run_id) or generated_at[:10]
    signals = _build_signals(data)
    source_cards = _build_source_cards(data)
    top_items = _build_top_items(signals, source_cards)
    traffic_light = _traffic_light(data, top_items, source_cards)
    project_impacts = build_project_impact_map(
        signals=signals,
        source_cards=source_cards,
        project_map=project_map,
        run_id=run_id,
        generated_at_utc=generated_at,
    )
    suggested_actions = _build_suggested_manual_actions(signals, traffic_light)
    hag = _build_hag_status(data)
    impacted_projects = [
        impact["display_name"]
        for impact in project_impacts["impacts"]
        if impact["impact_level"] != "none"
    ]
    human_brief = {
        "schema_version": 1,
        "brief_type": "human_daily_brief",
        "date": brief_date,
        "run_id": run_id,
        "generated_at_utc": generated_at,
        "overall_status": _overall_status(data),
        "traffic_light": traffic_light,
        "one_sentence_summary": _one_sentence_summary(
            traffic_light,
            top_items,
            source_cards,
            impacted_projects,
        ),
        "top_items": top_items,
        "source_cards": source_cards,
        "project_impacts": project_impacts["impacts"],
        "impacted_projects": impacted_projects,
        "suggested_manual_actions": suggested_actions,
        "urgent_action_count": _urgent_action_count(suggested_actions),
        "useful_item_count": len([item for item in top_items if item["kind"] != "empty"]),
        "manual_review_source_count": len(
            [source for source in source_cards if source["manual_review_required"]]
        ),
        "hag_status": hag,
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "evidence_paths": data["evidence_paths"],
        "no_runtime_llm": True,
        "no_auto_action": True,
        "manual_only": True,
    }
    ai_packet = {
        "schema_version": 1,
        "packet_type": "daily_intelligence_ai_model_packet",
        "date": brief_date,
        "run_id": run_id,
        "generated_at_utc": generated_at,
        "overall_status": human_brief["overall_status"],
        "facts": _build_facts(data, human_brief),
        "inferences": _build_inferences(human_brief, project_impacts),
        "project_impacts": project_impacts["impacts"],
        "suggested_prompts": _build_suggested_prompts(data, human_brief),
        "forbidden_actions": list(FORBIDDEN_ACTIONS),
        "evidence_paths": data["evidence_paths"],
        "confidence": _confidence(data, top_items, source_cards),
        "manual_only": True,
        "no_runtime_llm": True,
    }
    return {
        "schema_version": 1,
        "date": brief_date,
        "run_id": run_id,
        "generated_at_utc": generated_at,
        "human_brief": human_brief,
        "ai_model_packet": ai_packet,
        "project_impact_map": project_impacts,
    }


def write_daily_intelligence_outputs(
    *,
    bridge_root: str | Path = DEFAULT_BRIDGE_ROOT,
    run_id: str = "latest",
    output_dir: str | Path | None = None,
    project_map_path: str | Path = DEFAULT_PROJECT_IMPACT_MAP_PATH,
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    """Write daily brief Markdown and JSON outputs to the Bridge."""
    bridge = Path(bridge_root).expanduser().resolve()
    run_dir = resolve_run_dir(bridge, run_id)
    if run_dir is None:
        raise ValueError(f"run not found: {run_id}")
    target_dir = _outside_repo_output_dir(output_dir or bridge / DAILY_BRIEFS_DIRNAME)
    packet = build_daily_intelligence(
        run_dir,
        project_map_path=project_map_path,
        generated_at_utc=generated_at_utc,
    )
    date = str(packet["date"])
    safe_run_id = _safe_filename_part(str(packet["run_id"]))
    base = f"{date}-{safe_run_id}"
    human_json_path = target_dir / f"{base}-Human_Brief.json"
    human_md_path = target_dir / f"{base}-Human_Brief.md"
    ai_json_path = target_dir / f"{base}-AI_Model_Packet.json"
    ai_md_path = target_dir / f"{base}-AI_Model_Packet.md"
    impact_json_path = target_dir / f"{base}-Project_Impact_Map.json"
    write_json(human_json_path, packet["human_brief"])
    human_md_path.write_text(
        render_human_brief_markdown(packet["human_brief"]),
        encoding="utf-8",
        newline="\n",
    )
    write_json(ai_json_path, packet["ai_model_packet"])
    ai_md_path.write_text(
        render_ai_model_packet_markdown(packet["ai_model_packet"]),
        encoding="utf-8",
        newline="\n",
    )
    write_json(impact_json_path, packet["project_impact_map"])
    return {
        "status": "PASS",
        "run_id": packet["run_id"],
        "date": packet["date"],
        "output_dir": str(target_dir),
        "human_brief_markdown": str(human_md_path),
        "human_brief_json": str(human_json_path),
        "ai_model_packet_markdown": str(ai_md_path),
        "ai_model_packet_json": str(ai_json_path),
        "project_impact_map_json": str(impact_json_path),
        "no_auto_action": True,
        "no_runtime_llm": True,
        "manual_only": True,
    }


def build_daily_intelligence_for_bridge(
    bridge_root: str | Path,
    *,
    run_id: str = "latest",
    project_map_path: str | Path = DEFAULT_PROJECT_IMPACT_MAP_PATH,
) -> dict[str, object]:
    """Build a read-only in-memory brief for the web app."""
    bridge = Path(bridge_root).expanduser().resolve()
    run_dir = resolve_run_dir(bridge, run_id)
    if run_dir is None:
        raise ValueError(f"run not found: {run_id}")
    return build_daily_intelligence(run_dir, project_map_path=project_map_path)


def resolve_run_dir(bridge_root: str | Path, run_id: str) -> Path | None:
    """Resolve latest or explicit daily-sim run directory under Bridge/runs."""
    if not run_id.strip():
        return None
    root = Path(bridge_root).expanduser().resolve() / "runs"
    if _has_forbidden_path_part(root):
        return None
    if run_id == "latest":
        candidates = [
            child
            for child in root.iterdir()
            if child.is_dir()
            and child.name.startswith(DAILY_SIM_DIR_PREFIX)
            and not _has_forbidden_path_part(child)
        ] if root.is_dir() else []
        return sorted(candidates, key=lambda path: path.name, reverse=True)[0] if candidates else None
    if run_id.startswith(FORBIDDEN_PREFIXES) or "/" in run_id or "\\" in run_id:
        return None
    candidate = root / run_id
    return candidate if candidate.is_dir() and not _has_forbidden_path_part(candidate) else None


def load_project_impact_map(path: str | Path = DEFAULT_PROJECT_IMPACT_MAP_PATH) -> dict[str, Any]:
    """Load the configurable Project Impact Map used by Daily Intelligence."""
    data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError("ProjectImpactMap must be a dict.")
    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError("ProjectImpactMap.projects must be a non-empty list.")
    seen: set[str] = set()
    normalized_projects: list[dict[str, Any]] = []
    for index, raw in enumerate(projects):
        if not isinstance(raw, dict):
            raise ValueError(f"projects[{index}] must be a dict.")
        project_id = _required_str(raw, "project_id")
        if project_id in seen:
            raise ValueError(f"duplicate project_id: {project_id}")
        seen.add(project_id)
        keywords = _required_str_list(raw, "keywords")
        impact_types = _required_str_list(raw, "impact_types")
        priority = raw.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool) or priority < 1:
            raise ValueError("priority must be a positive integer.")
        normalized_projects.append(
            {
                "project_id": project_id,
                "display_name": _required_str(raw, "display_name"),
                "keywords": sorted(set(keyword.lower() for keyword in keywords)),
                "impact_types": sorted(set(impact_types)),
                "default_action": _required_str(raw, "default_action"),
                "priority": priority,
            }
        )
    return {
        "schema_version": data.get("schema_version", 1),
        "impact_scale": data.get("impact_scale", ["none", "low", "medium", "high"]),
        "projects": normalized_projects,
    }


def build_project_impact_map(
    *,
    signals: list[dict[str, Any]],
    source_cards: list[dict[str, Any]],
    project_map: dict[str, Any],
    run_id: str,
    generated_at_utc: str,
) -> dict[str, object]:
    """Compute deterministic project impacts from brief signals."""
    source_text = " ".join(
        [
            _signal_text(signal)
            for signal in signals
        ]
        + [
            f"{source.get('source_id')} {source.get('title')} {source.get('status')}"
            for source in source_cards
        ]
    ).lower()
    impacts: list[dict[str, object]] = []
    for project in sorted(project_map["projects"], key=lambda item: (item["priority"], item["project_id"])):
        project_id = str(project["project_id"])
        display_name = str(project["display_name"])
        exact_signals = [
            signal
            for signal in signals
            if _same_project(signal, project_id, display_name)
        ]
        keyword_matches = [
            keyword
            for keyword in project["keywords"]
            if keyword and keyword.lower() in source_text
        ]
        if exact_signals:
            level = _highest_level_for_signals(exact_signals)
            certainty = "certain"
            reason = "target project was named by an action or prompt signal"
        elif keyword_matches:
            level = "medium" if len(keyword_matches) >= 2 else "low"
            certainty = "potential"
            reason = f"keyword match: {', '.join(keyword_matches[:5])}"
        else:
            level = "none"
            certainty = "none"
            reason = "no project keyword or target-project match"
        impacts.append(
            {
                "project_id": project_id,
                "display_name": display_name,
                "impact_level": level,
                "impact_score": {"none": 0, "low": 1, "medium": 2, "high": 3}[level],
                "certainty": certainty,
                "keyword_matches": keyword_matches,
                "impact_types": list(project["impact_types"]),
                "reason": reason,
                "default_action": project["default_action"],
                "manual_only": True,
            }
        )
    return {
        "schema_version": 1,
        "map_type": "daily_intelligence_project_impact_map",
        "run_id": run_id,
        "generated_at_utc": generated_at_utc,
        "impact_scale": ["none", "low", "medium", "high"],
        "impacts": impacts,
        "manual_only": True,
    }


def render_human_brief_markdown(brief: object) -> str:
    """Render Human Daily Brief Markdown."""
    data = _mapping(brief)
    traffic = _mapping(data.get("traffic_light"))
    hag = _mapping(data.get("hag_status"))
    lines = [
        f"# Daily Intelligence Brief - {data.get('date')}",
        "",
        "## Oggi in 30 secondi",
        "",
        f"- [F] run_id: {data.get('run_id')}.",
        f"- [F] generated_at_utc: {data.get('generated_at_utc')}.",
        f"- [F] semaforo: {traffic.get('label')} ({traffic.get('color')}).",
        f"- [F] sintesi: {data.get('one_sentence_summary')}",
        f"- [F] novita_utili: {data.get('useful_item_count')}.",
        f"- [F] azioni_urgenti: {data.get('urgent_action_count')}.",
        f"- [F] fonti_manual_review: {data.get('manual_review_source_count')}.",
        f"- [F] HAG: {hag.get('status')} - preserved={str(hag.get('preserved')).lower()}.",
        "",
        "## Top novita",
        "",
    ]
    for item in _list(data.get("top_items")):
        item_data = _mapping(item)
        lines.append(
            f"- [F] {item_data.get('title')} | fonte={item_data.get('source')} | "
            f"stato={item_data.get('status')} | evidenza={item_data.get('evidence_ref')}"
        )
    lines.extend(["", "## Fonti controllate", ""])
    for source in _list(data.get("source_cards")):
        source_data = _mapping(source)
        lines.append(
            f"- [F] {source_data.get('source_id')}: {source_data.get('status')}; "
            f"manual_review={str(source_data.get('manual_review_required')).lower()}; "
            f"items={source_data.get('item_count')}; evidenza={source_data.get('evidence_ref')}"
        )
    lines.extend(["", "## Impatto sui progetti", ""])
    impacted = [
        _mapping(impact)
        for impact in _list(data.get("project_impacts"))
        if _mapping(impact).get("impact_level") != "none"
    ]
    if impacted:
        for impact in impacted:
            lines.append(
                f"- [INT] {impact.get('display_name')}: {impact.get('impact_level')} "
                f"({impact.get('certainty')}); motivo={impact.get('reason')}; "
                f"azione_manual_only={impact.get('default_action')}"
            )
    else:
        lines.append("- [INT] Nessun impatto progetto rilevato oltre la soglia minima.")
    lines.extend(["", "## Azioni consigliate manual-only", ""])
    for action in _list(data.get("suggested_manual_actions")):
        action_data = _mapping(action)
        lines.append(
            f"- [PROP] {action_data.get('title')}; manual_only="
            f"{str(action_data.get('manual_only')).lower()}; "
            f"not_executed={str(action_data.get('not_executed')).lower()}."
        )
    lines.extend(
        [
            "",
            "## HAG e azioni vietate",
            "",
            f"- [F] HAG preserved: {str(hag.get('preserved')).lower()}.",
            "- [F] Nessuna azione automatica, email, notifica, scheduler mutation o chiamata LLM runtime.",
            "- [F] Azioni vietate: " + ", ".join(str(item) for item in _list(data.get("forbidden_actions"))) + ".",
        ]
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def render_ai_model_packet_markdown(packet: object) -> str:
    """Render the AI Model Packet as Markdown."""
    data = _mapping(packet)
    lines = [
        f"# AI Model Packet - {data.get('date')}",
        "",
        "## Scope",
        "",
        f"- [F] packet_type: {data.get('packet_type')}.",
        f"- [F] run_id: {data.get('run_id')}.",
        f"- [F] generated_at_utc: {data.get('generated_at_utc')}.",
        "- [F] This packet is manual-only and was generated without runtime LLM calls.",
        "",
        "## Facts",
        "",
    ]
    for fact in _list(data.get("facts")):
        fact_data = _mapping(fact)
        lines.append(f"- [F] {fact_data.get('statement')} Fonte: {fact_data.get('source')}.")
    lines.extend(["", "## Inferences", ""])
    for inference in _list(data.get("inferences")):
        inference_data = _mapping(inference)
        lines.append(
            f"- [INT] {inference_data.get('statement')} "
            f"Confidence: {inference_data.get('confidence')}."
        )
    lines.extend(["", "## Suggested Manual Prompts", ""])
    for prompt in _list(data.get("suggested_prompts")):
        prompt_data = _mapping(prompt)
        lines.append(
            f"- [PROP] {prompt_data.get('title')}: {prompt_data.get('prompt')} "
            f"manual_only={str(prompt_data.get('manual_only')).lower()}."
        )
    lines.extend(
        [
            "",
            "## Forbidden Actions",
            "",
            "- [F] " + ", ".join(str(item) for item in _list(data.get("forbidden_actions"))) + ".",
        ]
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def _load_run_data(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise ValueError(f"run_dir not found: {root}")
    files = {
        "daily_summary": root / "0350-Daily_Sim_Summary.json",
        "run_summary": root / "0180-Run_Summary.json",
        "quality_gate": root / "0630-Daily_Quality_Gate_V2.json",
        "action_triage": root / "0650-Action_Triage.json",
        "prompt_suggestions": root / "0660-Codex_Prompt_Suggestions.json",
        "compact_report": root / "0180-Report_Compact.md",
        "hag_report": root / "0680-Human_Approval_Gate_Report.md",
    }
    data: dict[str, Any] = {"run_dir": str(root), "evidence_paths": [], "warnings": []}
    for key, path in files.items():
        if _has_forbidden_path_part(path):
            data["warnings"].append(f"forbidden_path_name:{path.name}")
            data[key] = {}
            continue
        if not path.is_file():
            data["warnings"].append(f"missing:{path.name}")
            data[key] = {}
            continue
        data["evidence_paths"].append(str(path))
        if path.suffix == ".json":
            try:
                value = read_json(path)
            except (OSError, ValueError) as exc:
                data["warnings"].append(f"read_error:{path.name}:{exc}")
                value = {}
            data[key] = value if isinstance(value, dict) else {}
        else:
            try:
                data[key] = path.read_text(encoding="utf-8")
            except OSError as exc:
                data["warnings"].append(f"read_error:{path.name}:{exc}")
                data[key] = ""
    return data


def _build_signals(data: dict[str, Any]) -> list[dict[str, Any]]:
    daily = _mapping(data.get("daily_summary"))
    action_triage = _mapping(daily.get("action_triage") or data.get("action_triage"))
    prompt_suggestions = _mapping(daily.get("prompt_suggestions") or data.get("prompt_suggestions"))
    signals: list[dict[str, Any]] = []
    for index, raw in enumerate(_list(action_triage.get("entries"))):
        item = _mapping(raw)
        if not item:
            continue
        signals.append(
            {
                "signal_id": f"action-{index + 1}",
                "signal_type": "action_triage",
                "title": _text(item.get("title") or item.get("source_id") or "Radar action"),
                "summary": _text(item.get("reason") or item.get("summary") or item.get("triage_class")),
                "status": _text(item.get("triage_class") or action_triage.get("status") or "NO_DATA"),
                "category": _text(item.get("item_category") or item.get("category") or ""),
                "source": _text(item.get("source_id") or "Action triage"),
                "target_project": _text(item.get("target_project") or item.get("project_name") or ""),
                "project_key": _text(item.get("project_key") or ""),
                "risk_class": _text(item.get("risk_class") or item.get("risk_level") or ""),
                "score": item.get("score"),
                "evidence_ref": _evidence_ref(data, "action_triage"),
                "manual_only": True,
            }
        )
    for index, raw in enumerate(_list(prompt_suggestions.get("suggestions"))):
        item = _mapping(raw)
        if not item:
            continue
        signals.append(
            {
                "signal_id": f"prompt-{index + 1}",
                "signal_type": "manual_prompt_suggestion",
                "title": _text(item.get("title") or "Manual prompt suggestion"),
                "summary": _text(item.get("reason") or item.get("status") or "suggested_only"),
                "status": _text(item.get("status") or prompt_suggestions.get("status") or "suggested_only"),
                "category": _text(item.get("risk_class") or ""),
                "source": "Prompt suggestions",
                "target_project": _text(item.get("target_project") or ""),
                "project_key": _text(item.get("project_key") or ""),
                "risk_class": _text(item.get("risk_class") or ""),
                "score": item.get("score"),
                "evidence_ref": _evidence_ref(data, "prompt_suggestions"),
                "manual_only": True,
            }
        )
    real_run = _real_run(data)
    item_count = _int(real_run.get("item_count"))
    if not signals and item_count:
        signals.append(
            {
                "signal_id": "run-items",
                "signal_type": "run_summary",
                "title": f"{item_count} radar item(s) available",
                "summary": "Run contains parsed items, but no action triage entry was available.",
                "status": _overall_status(data),
                "category": "",
                "source": "Run summary",
                "target_project": "",
                "project_key": "",
                "risk_class": "",
                "score": None,
                "evidence_ref": _evidence_ref(data, "run_summary"),
                "manual_only": True,
            }
        )
    return signals


def _build_source_cards(data: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, raw in enumerate(_list(_real_run(data).get("source_diagnostics"))):
        source = _mapping(raw)
        if not source:
            continue
        status = _text(source.get("diagnostic_status") or source.get("fetch_status") or "NO_DATA")
        cards.append(
            {
                "source_id": _text(source.get("source_id") or f"source-{index + 1}"),
                "provider": _text(source.get("provider") or "unknown"),
                "status": status,
                "manual_review_required": source.get("manual_review_required") is True
                or status == "manual_review_required"
                or source.get("http_status_code") == 403
                or source.get("http_status") == 403,
                "http_status": source.get("http_status_code") or source.get("http_status"),
                "item_count": _int(source.get("item_count")),
                "follow_up": _text(source.get("recommended_follow_up") or ""),
                "title": _source_title(source),
                "evidence_ref": _evidence_ref(data, "run_summary"),
            }
        )
    return cards


def _build_top_items(
    signals: list[dict[str, Any]],
    source_cards: list[dict[str, Any]],
    *,
    limit: int = 5,
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for signal in signals:
        items.append(
            {
                "kind": signal["signal_type"],
                "title": signal["title"],
                "source": signal["source"],
                "status": signal["status"],
                "why_it_matters": signal["summary"],
                "manual_only": True,
                "evidence_ref": signal["evidence_ref"],
            }
        )
        if len(items) >= limit:
            return items
    for source in source_cards:
        if not source["manual_review_required"]:
            continue
        items.append(
            {
                "kind": "source_manual_review",
                "title": source["title"],
                "source": source["source_id"],
                "status": source["status"],
                "why_it_matters": "Source requires manual review before depending on it.",
                "manual_only": True,
                "evidence_ref": source["evidence_ref"],
            }
        )
        if len(items) >= limit:
            return items
    if not items:
        items.append(
            {
                "kind": "empty",
                "title": "Nessuna novita importante",
                "source": "Daily run",
                "status": "NO_ACTION_REQUIRED",
                "why_it_matters": "No action signal was detected in the available run artifacts.",
                "manual_only": True,
                "evidence_ref": "",
            }
        )
    return items


def _build_suggested_manual_actions(
    signals: list[dict[str, Any]],
    traffic_light: dict[str, object],
) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    for signal in signals:
        if signal["signal_type"] == "manual_prompt_suggestion":
            title = f"Review manual prompt suggestion: {signal['title']}"
        else:
            title = f"Review signal manually: {signal['title']}"
        actions.append(
            {
                "title": title,
                "reason": signal["summary"],
                "priority": _action_priority(signal, traffic_light),
                "manual_only": True,
                "not_executed": True,
                "forbidden_to_execute_automatically": True,
                "evidence_ref": signal["evidence_ref"],
            }
        )
    if not actions:
        actions.append(
            {
                "title": "Nessuna azione manuale urgente",
                "reason": "The brief contains no direct action signal.",
                "priority": "none",
                "manual_only": True,
                "not_executed": True,
                "forbidden_to_execute_automatically": True,
                "evidence_ref": "",
            }
        )
    return actions


def _build_facts(data: dict[str, Any], brief: dict[str, Any]) -> list[dict[str, object]]:
    real_run = _real_run(data)
    facts = [
        {
            "fact_id": "run.status",
            "statement": f"Run {brief['run_id']} has status {brief['overall_status']}.",
            "source": _evidence_ref(data, "daily_summary"),
        },
        {
            "fact_id": "run.sources",
            "statement": (
                f"Sources checked: {_int(real_run.get('source_count'))}; "
                f"parsed: {_int(real_run.get('parsed_count'))}."
            ),
            "source": _evidence_ref(data, "run_summary"),
        },
        {
            "fact_id": "brief.hag",
            "statement": f"HAG status is {_mapping(brief.get('hag_status')).get('status')}.",
            "source": _evidence_ref(data, "daily_summary"),
        },
        {
            "fact_id": "brief.actions",
            "statement": (
                f"Manual suggested actions: {len(_list(brief.get('suggested_manual_actions')))}; "
                "none were executed."
            ),
            "source": _evidence_ref(data, "action_triage"),
        },
    ]
    return facts


def _build_inferences(
    brief: dict[str, Any],
    project_impacts: dict[str, object],
) -> list[dict[str, object]]:
    impacted = [
        _mapping(impact)
        for impact in _list(project_impacts.get("impacts"))
        if _mapping(impact).get("impact_level") != "none"
    ]
    return [
        {
            "inference_id": "traffic_light",
            "statement": (
                f"Daily traffic light is {_mapping(brief.get('traffic_light')).get('label')} "
                "based on action, HAG and source warning signals."
            ),
            "confidence": _mapping(brief.get("traffic_light")).get("confidence"),
            "basis": "deterministic status and count mapping",
        },
        {
            "inference_id": "project_impacts",
            "statement": f"{len(impacted)} project(s) may be impacted.",
            "confidence": 0.74 if impacted else 0.68,
            "basis": "configured keyword and target-project map",
        },
    ]


def _build_suggested_prompts(
    data: dict[str, Any],
    brief: dict[str, Any],
) -> list[dict[str, object]]:
    prompt_data = _mapping(
        _mapping(data.get("daily_summary")).get("prompt_suggestions")
        or data.get("prompt_suggestions")
    )
    suggestions = _list(prompt_data.get("suggestions"))
    prompts: list[dict[str, object]] = []
    for index, raw in enumerate(suggestions):
        suggestion = _mapping(raw)
        title = _text(suggestion.get("title") or f"Manual prompt {index + 1}")
        prompts.append(
            {
                "title": title,
                "prompt": (
                    "Use the attached AI Model Packet as evidence. Separate facts from "
                    "inferences and propose only manual next steps."
                ),
                "manual_only": True,
                "not_executed": True,
                "source": _evidence_ref(data, "prompt_suggestions"),
            }
        )
    if not prompts:
        prompts.append(
            {
                "title": "Manual daily brief review",
                "prompt": (
                    f"Review run {brief['run_id']} using the facts and inferences in this packet. "
                    "Do not execute actions, send messages, mutate scheduler state or bypass HAG."
                ),
                "manual_only": True,
                "not_executed": True,
                "source": _evidence_ref(data, "daily_summary"),
            }
        )
    return prompts


def _traffic_light(
    data: dict[str, Any],
    top_items: list[dict[str, object]],
    source_cards: list[dict[str, Any]],
) -> dict[str, object]:
    daily = _mapping(data.get("daily_summary"))
    statuses = " ".join(
        _text(value).upper()
        for value in (
            daily.get("status"),
            daily.get("automation_gate_status"),
            _mapping(daily.get("daily_quality_gate_v2")).get("overall_daily_review_status"),
            _mapping(daily.get("action_triage")).get("status"),
            daily.get("hag_status"),
        )
    )
    source_warnings = [source for source in source_cards if source["manual_review_required"]]
    actionable_items = [item for item in top_items if item.get("kind") != "empty"]
    if any(token in statuses for token in ("FAIL", "BLOCKED", "CRITICAL")):
        return _traffic("red", "Rosso", "Blocking or critical signal present.", 0.86)
    if "HOLD" in statuses and actionable_items:
        return _traffic("red", "Rosso", "HAG hold with action signal present.", 0.84)
    if actionable_items or source_warnings or "WARNING" in statuses or "WARN" in statuses:
        return _traffic("yellow", "Giallo", "Manual review or useful news present.", 0.78)
    if "PASS" in statuses:
        return _traffic("green", "Verde", "No immediate action signal detected.", 0.73)
    return _traffic("gray", "Grigio", "Insufficient data for a reliable daily brief.", 0.62)


def _traffic(color: str, label: str, reason: str, confidence: float) -> dict[str, object]:
    return {"color": color, "label": label, "reason": reason, "confidence": confidence}


def _one_sentence_summary(
    traffic_light: dict[str, object],
    top_items: list[dict[str, object]],
    source_cards: list[dict[str, Any]],
    impacted_projects: list[str],
) -> str:
    useful_count = len([item for item in top_items if item.get("kind") != "empty"])
    manual_sources = len([source for source in source_cards if source["manual_review_required"]])
    if traffic_light["color"] == "green":
        return "Nessuna novita importante: il radar non propone azioni immediate."
    if traffic_light["color"] == "gray":
        return "Dati insufficienti: apri Expert Mode per verificare gli artifact mancanti."
    project_text = ", ".join(impacted_projects[:3]) if impacted_projects else "nessun progetto specifico"
    return (
        f"{useful_count} novita utili, {manual_sources} fonti da controllare, "
        f"impatto potenziale su {project_text}; decisione solo umana."
    )


def _build_hag_status(data: dict[str, Any]) -> dict[str, object]:
    daily = _mapping(data.get("daily_summary"))
    status = _text(daily.get("hag_status") or "NO_DATA")
    return {
        "status": status,
        "preserved": True,
        "message": "HAG preserved: the brief proposes and does not execute.",
        "no_bypass": True,
    }


def _confidence(
    data: dict[str, Any],
    top_items: list[dict[str, object]],
    source_cards: list[dict[str, Any]],
) -> dict[str, object]:
    warnings = _list(data.get("warnings"))
    if not top_items or top_items[0].get("kind") == "empty":
        value = 0.68
    elif warnings:
        value = 0.72
    elif source_cards:
        value = 0.78
    else:
        value = 0.74
    return {
        "score": value,
        "rationale": "Deterministic packet from local run artifacts; lower when data is missing.",
        "warnings": warnings,
    }


def _overall_status(data: dict[str, Any]) -> str:
    daily = _mapping(data.get("daily_summary"))
    real_run = _real_run(data)
    return _text(daily.get("status") or real_run.get("status") or "NO_DATA")


def _real_run(data: dict[str, Any]) -> dict[str, Any]:
    daily = _mapping(data.get("daily_summary"))
    run_summary = _mapping(data.get("run_summary"))
    return _mapping(daily.get("real_run") or run_summary.get("result"))


def _source_title(source: dict[str, Any]) -> str:
    source_id = _text(source.get("source_id") or "source")
    if source.get("manual_review_required") is True or source.get("http_status_code") == 403:
        return f"Manual review source: {source_id}"
    status = _text(source.get("diagnostic_status") or source.get("fetch_status") or "NO_DATA")
    return f"{source_id}: {status}"


def _same_project(signal: dict[str, Any], project_id: str, display_name: str) -> bool:
    project_key = _text(signal.get("project_key")).lower()
    target_project = _text(signal.get("target_project")).lower()
    return (
        project_key == project_id.lower()
        or target_project == display_name.lower()
        or target_project.replace(" ", "_") == project_id.lower()
    )


def _highest_level_for_signals(signals: list[dict[str, Any]]) -> str:
    text = " ".join(_signal_text(signal) for signal in signals).upper()
    if any(token in text for token in ("BLOCKED", "HOLD", "HIGH", "L2", "CRITICAL")):
        return "high"
    if any(token in text for token in ("CANDIDATE", "PROMPT", "DIRECT", "REVIEW")):
        return "medium"
    return "low"


def _signal_text(signal: dict[str, Any]) -> str:
    return " ".join(
        _text(signal.get(key))
        for key in (
            "title",
            "summary",
            "status",
            "category",
            "source",
            "target_project",
            "project_key",
            "risk_class",
        )
    )


def _action_priority(signal: dict[str, Any], traffic_light: dict[str, object]) -> str:
    text = _signal_text(signal).upper()
    if traffic_light["color"] == "red" or any(token in text for token in ("BLOCKED", "HOLD", "HIGH")):
        return "high"
    if traffic_light["color"] == "yellow":
        return "medium"
    return "low"


def _urgent_action_count(actions: list[dict[str, object]]) -> int:
    return len([action for action in actions if action.get("priority") == "high"])


def _evidence_ref(data: dict[str, Any], key: str) -> str:
    path_by_key = {
        "daily_summary": "0350-Daily_Sim_Summary.json",
        "run_summary": "0180-Run_Summary.json",
        "action_triage": "0650-Action_Triage.json",
        "prompt_suggestions": "0660-Codex_Prompt_Suggestions.json",
    }
    suffix = path_by_key.get(key)
    if not suffix:
        return ""
    for path in _list(data.get("evidence_paths")):
        if str(path).endswith(suffix):
            return str(path)
    return suffix


def _outside_repo_output_dir(path: str | Path) -> Path:
    target = Path(path).expanduser().resolve()
    if _is_path_within(target, REPO_ROOT):
        raise ValueError("daily brief output_dir must be outside repository.")
    if _has_forbidden_path_part(target):
        raise ValueError("daily brief output_dir must not use LAST-* or latest-* names.")
    target.mkdir(parents=True, exist_ok=True)
    return target


def _date_from_run_id(run_id: str) -> str | None:
    match = re.search(r"(\d{8})_\d{6}", run_id)
    if not match:
        return None
    stamp = match.group(1)
    return f"{stamp[0:4]}-{stamp[4:6]}-{stamp[6:8]}"


def _safe_filename_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "run"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _required_str(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _required_str_list(data: dict[str, Any], field_name: str) -> list[str]:
    value = data.get(field_name)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list.")
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string.")
        result.append(item)
    return result


def _has_forbidden_path_part(path: Path) -> bool:
    return any(part.startswith(FORBIDDEN_PREFIXES) for part in path.parts)


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object) -> str:
    return str(value).strip() if value is not None else ""


def _int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
