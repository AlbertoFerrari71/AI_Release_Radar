import unittest
from pathlib import Path

from radar.json_utils import read_json
from radar.source_registry import (
    MANDATORY_SOURCE_FIELDS,
    SourceDefinition,
    load_source_registry,
    load_source_registry_file,
    source_registry_to_dict,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
VALID_FIXTURE_PATH = FIXTURES_DIR / "0100_openai_sources_valid.json"
INVALID_FIXTURE_PATH = FIXTURES_DIR / "0100_openai_sources_invalid.json"
CONFIG_PATH = REPO_ROOT / "config" / "sources" / "openai_sources.json"


class SourceRegistryTests(unittest.TestCase):
    def test_loads_valid_registry_fixture(self):
        sources = load_source_registry(read_json(VALID_FIXTURE_PATH))
        self.assertGreaterEqual(len(sources), 6)
        self.assertTrue(all(isinstance(source, SourceDefinition) for source in sources))

    def test_valid_sources_have_all_mandatory_fields(self):
        sources = load_source_registry(read_json(VALID_FIXTURE_PATH))
        for source in sources:
            data = source.to_dict()
            self.assertEqual(set(data), set(MANDATORY_SOURCE_FIELDS))
            for field_name in MANDATORY_SOURCE_FIELDS:
                self.assertIn(field_name, data)

    def test_missing_mandatory_field_fails(self):
        source = self.valid_source_dict()
        del source["notes"]
        with self.assertRaisesRegex(ValueError, "notes is required"):
            load_source_registry(self.registry_for(source))

    def test_invalid_source_id_fails(self):
        with self.assertRaisesRegex(ValueError, "source_id"):
            load_source_registry(self.registry_for(self.invalid_source("invalid_source_id")))

    def test_non_https_url_fails(self):
        with self.assertRaisesRegex(ValueError, "https"):
            load_source_registry(self.registry_for(self.invalid_source("non_https_url")))

    def test_priority_less_than_one_fails(self):
        with self.assertRaisesRegex(ValueError, "priority"):
            load_source_registry(self.registry_for(self.invalid_source("priority_less_than_one")))

    def test_invalid_source_type_fails(self):
        with self.assertRaisesRegex(ValueError, "source_type"):
            load_source_registry(self.registry_for(self.invalid_source("invalid_source_type")))

    def test_invalid_reliability_fails(self):
        with self.assertRaisesRegex(ValueError, "reliability"):
            load_source_registry(self.registry_for(self.invalid_source("invalid_reliability")))

    def test_invalid_verification_status_fails(self):
        with self.assertRaisesRegex(ValueError, "verification_status"):
            load_source_registry(
                self.registry_for(self.invalid_source("invalid_verification_status"))
            )

    def test_registry_is_sorted_deterministically(self):
        valid = read_json(VALID_FIXTURE_PATH)
        shuffled = dict(valid)
        shuffled["sources"] = list(reversed(valid["sources"]))
        sources = load_source_registry(shuffled)
        keys = [(source.priority, source.source_id) for source in sources]
        self.assertEqual(keys, sorted(keys))

        serialized = source_registry_to_dict(list(reversed(sources)))
        serialized_keys = [
            (source["priority"], source["source_id"]) for source in serialized["sources"]
        ]
        self.assertEqual(serialized_keys, sorted(serialized_keys))

    def test_config_openai_sources_json_is_valid(self):
        sources = load_source_registry_file(str(CONFIG_PATH))
        source_ids = {source.source_id for source in sources}
        self.assertIn("openai_codex_changelog", source_ids)
        self.assertIn("github_api_openai_codex_releases", source_ids)
        self.assertGreaterEqual(len(sources), 11)

    def valid_source_dict(self):
        return read_json(VALID_FIXTURE_PATH)["sources"][0]

    def invalid_source(self, case_id: str):
        fixture = read_json(INVALID_FIXTURE_PATH)
        for case in fixture["cases"]:
            if case["case_id"] == case_id:
                return case["source"]
        raise AssertionError(f"Missing invalid fixture case: {case_id}")

    def registry_for(self, source: dict):
        return {
            "schema_version": 1,
            "provider": "openai",
            "sources": [source],
        }


if __name__ == "__main__":
    unittest.main()
