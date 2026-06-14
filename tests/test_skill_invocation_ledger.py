import json
import tempfile
import unittest
from pathlib import Path

from radar.skill_ledger import (
    VALID_RESULTS,
    parse_skill_invocation_jsonl,
    validate_skill_invocation_record,
)


class SkillInvocationLedgerTests(unittest.TestCase):
    def sample_record(self, *, result: str = "used") -> dict[str, object]:
        return {
            "timestamp_utc": "2026-06-14T08:00:00Z",
            "project": "AI_Release_Radar",
            "repo_path": r"C:\Users\alberto.ferrari\source\repos\AI_Release_Radar",
            "step_id": "2460-2600",
            "process": "Daily Intelligence Brief",
            "phase": "2550",
            "skill_name": "as-common-web-ui-design-review",
            "skill_path": r"C:\Users\alberto.ferrari\.agents\skills\as-common-web-ui-design-review",
            "caller": "Codex",
            "purpose": "UI acceptance review guidance",
            "input_scope": "metadata-only",
            "output_scope": "Bridge report metadata",
            "result": result,
            "confidence": 0.9,
            "notes": "No sensitive content logged.",
        }

    def test_validates_allowed_results(self):
        for result in VALID_RESULTS:
            with self.subTest(result=result):
                record = validate_skill_invocation_record(self.sample_record(result=result))
                self.assertEqual(record["result"], result)

    def test_rejects_missing_fields_and_invalid_result(self):
        missing = self.sample_record()
        missing.pop("skill_name")
        with self.assertRaisesRegex(ValueError, "missing required"):
            validate_skill_invocation_record(missing)
        invalid = self.sample_record(result="done")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_skill_invocation_record(invalid)

    def test_parses_jsonl_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "skill_invocations.jsonl"
            records = [
                self.sample_record(result="used"),
                self.sample_record(result="skill_missing"),
            ]
            path.write_text(
                "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
                encoding="utf-8",
            )
            parsed = parse_skill_invocation_jsonl(path)

        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[1]["result"], "skill_missing")


if __name__ == "__main__":
    unittest.main()
