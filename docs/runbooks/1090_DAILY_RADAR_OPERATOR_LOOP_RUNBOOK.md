# 1090) Daily Radar Operator Loop Runbook

## A. Aprire La Dashboard

- [F] Avviare localmente con `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`.
- [F] Aprire `http://127.0.0.1:8787`. Fonte: default host/port in `radar_web/config.py`.
- [F] La dashboard resta locale e non richiede bind su `0.0.0.0`. Fonte: `radar_web/app.py`, `radar_web/config.py`.

## B. Leggere Action Center

- [F] La pagina Action Center e' `/actions`. Fonte: `radar_web/app.py`.
- [F] L'API Action Inbox e' `/api/actions`. Fonte: `radar_web/app.py`.
- [F] Ogni azione mostra project badge, project key, priority, risk, decision status, safety status, trend e noise status. Fonte: `radar_web/templates/actions.html`.
- [F] I dati derivano dai run Bridge gia' esistenti letti tramite `radar_web/run_locator.py`. Fonte: `radar_web/action_center.py`.

## C. Decidere Azioni

- [F] Le decisioni disponibili sono `approve_prompt`, `defer`, `ignore`, `backlog` e `request_review`. Fonte: `radar/action_inbox.py`.
- [F] Ogni decisione viene scritta nel decision log Bridge con `human_required=true` e `no_auto_action=true`. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Il decision log e' `action_dispatch/decision_log.jsonl` sotto il Bridge configurato. Fonte: `radar_web/action_center.py`.

## D. Significato Decisioni

- [F] `Approve prompt` abilita la generazione di un prompt pack Markdown nel Bridge, ma non lo esegue. Fonte: `radar/action_inbox.py`.
- [F] `Backlog` registra l'azione come backlog supervisionato e la include nell'export backlog. Fonte: `radar/action_inbox.py`.
- [F] `Ignore` mantiene evidenza e decisione, ma le regole noise impediscono che resti high priority. Fonte: `radar/action_inbox.py`.
- [F] `Defer` abbassa l'urgenza senza cancellare l'azione. Fonte: `radar/action_inbox.py`.
- [F] `Request review` registra una richiesta di review supervisionata e abilita solo output prompt Markdown. Fonte: `radar/action_inbox.py`.

## E. Prompt Pack Nel Bridge

- [F] Il prompt pack viene scritto in `action_dispatch/<run_id>/` sotto il Bridge configurato. Fonte: `radar/action_inbox.py`.
- [F] Il file prompt usa prefisso `1000-Prompt_` e suffisso `.md`. Fonte: `radar/action_inbox.py`.
- [F] Il prompt contiene contesto, fonte radar, novita', progetto target, rischio, obiettivo, vincoli, cosa non fare, test richiesti e output atteso. Fonte: `radar/action_inbox.py`.
- [F] Il prompt pack non viene copiato negli appunti e non viene lanciato. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.

## F. Non Eseguire Automaticamente Nulla

- [F] Il safety gate imposta auto-action, external repo write, LLM call, email e scheduler change come output bloccati. Fonte: `radar/action_inbox.py`.
- [F] La generazione prompt richiede una decisione umana esplicita. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] L'Action Center scrive solo file Bridge: decision log, prompt Markdown e backlog export. Fonte: `radar_web/action_center.py`.

## G. Uso Supervisionato Con Codex

- [PROP] Alberto apre il prompt pack Markdown nel Bridge, lo rivede, poi lo usa in una sessione Codex separata.
- [PROP] Ogni sessione Codex successiva deve rispettare il repo target, i test richiesti e i vincoli del prompt pack.
- [PROP] Se il prompt pack riguarda repo esterni, non usare questa dashboard per modificarli automaticamente.

## H. Troubleshooting Decision Log

- [F] Se il Bridge non e' scrivibile, l'API restituisce stato `WARN` o `REFUSED` con warning nel JSON. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Se il decision log non esiste, viene creato al primo append riuscito. Fonte: `radar/action_inbox.py`.
- [F] Se il decision log contiene righe JSON invalide, la lettura ignora quelle righe e continua. Fonte: `radar/action_inbox.py`.

## I. Troubleshooting Bridge Non Accessibile

- [F] `DashboardConfig.validate_output_root` segnala output root dentro repo o path con `LAST-*`/`latest-*`. Fonte: `radar_web/config.py`.
- [F] L'Action Center rifiuta scritture se l'action dispatch root non supera la validazione. Fonte: `radar_web/action_center.py`.
- [PROP] Se il Bridge e' assente, verificare il percorso configurato in `radar_web/config.py` e rilanciare la dashboard.
