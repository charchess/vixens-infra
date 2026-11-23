import copy
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts/durable-custody-ledger-adapter-v1.yaml"
FIXTURE = ROOT / "tests/fixtures/durable-custody-ledger-adapter-v1.oracle.jcs.json"


def jcs(value):
    # The normative document contains only JSON-native strings, integers, bools,
    # nulls, arrays and objects; this is RFC 8785-compatible for that domain.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def load_yaml(path=CONTRACT):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_oracle():
    return json.loads(FIXTURE.read_bytes().decode("utf-8"))


def cross_references(candidate):
    spec = candidate["spec"]
    assert set(spec) == set(spec["oracle"]["topLevelSpecKeys"])
    operations = spec["operations"]
    assert set(operations) == set(spec["oracle"]["requiredOperations"])
    assert set(spec["fieldRules"]) == set(operations)
    references = set()
    for operation, definition in operations.items():
        fields = spec["fieldRules"][operation]
        assert set(fields) == {"input", "output", "refusal"}
        for direction, list_key in (("input", "inputFields"), ("output", "outputFields"), ("refusal", "refusalFields")):
            assert set(definition[list_key]) == set(fields[direction])
            for binding in fields[direction].values():
                assert set(binding) == set(spec["fieldRuleShape"]["requiredKeys"])
                assert binding["scalarRule"] in spec["scalarRules"]
                references.add(binding["scalarRule"])
    assert references == set(spec["scalarRules"])
    states = spec["scalarRules"]["state"]["enum"]
    assert set(spec["transitionTable"]) == set(states)
    for state, next_states in spec["transitionTable"].items():
        assert all(item in states for item in next_states)


def valid(candidate):
    try:
        oracle = load_oracle()
        if candidate != oracle:
            return False
        if jcs(candidate) != FIXTURE.read_bytes():
            return False
        cross_references(candidate)
        return True
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def walk(value, path=()):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (index,))


def at(root, path):
    for part in path:
        root = root[part]
    return root


def changed(value):
    if value is None:
        return "not-null"
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "-mutated"
    raise TypeError(type(value))


class DurableCustodyLedgerAdapterV1ContractTests(unittest.TestCase):
    def test_canonical_contract_fixture_and_cross_references_are_exact(self):
        contract = load_yaml()
        self.assertEqual(contract, load_oracle())
        self.assertEqual(jcs(contract), FIXTURE.read_bytes())
        cross_references(contract)
        self.assertTrue(valid(contract))

    def test_every_recursive_map_list_and_scalar_mutation_is_rejected(self):
        canonical = load_oracle()
        self.assertTrue(valid(canonical))
        cases = 0
        for path, node in list(walk(canonical)):
            if not path:
                continue
            parent_path, leaf = path[:-1], path[-1]
            if isinstance(node, dict):
                for key in list(node):
                    mutated = copy.deepcopy(canonical)
                    del at(mutated, path)[key]
                    self.assertFalse(valid(mutated), (path, "remove", key)); cases += 1
                    mutated = copy.deepcopy(canonical)
                    at(mutated, path)[key + "Unknown"] = copy.deepcopy(node[key])
                    self.assertFalse(valid(mutated), (path, "add", key)); cases += 1
                    mutated = copy.deepcopy(canonical)
                    value = at(mutated, path).pop(key)
                    at(mutated, path)[key + "Renamed"] = value
                    self.assertFalse(valid(mutated), (path, "rename", key)); cases += 1
                for replacement in ("invalid", [], None):
                    mutated = copy.deepcopy(canonical)
                    target = at(mutated, parent_path)
                    target[leaf] = replacement
                    self.assertFalse(valid(mutated), (path, "replace-map")); cases += 1
            elif isinstance(node, list):
                for index in range(len(node)):
                    mutated = copy.deepcopy(canonical); del at(mutated, path)[index]
                    self.assertFalse(valid(mutated), (path, "remove", index)); cases += 1
                    mutated = copy.deepcopy(canonical); at(mutated, path).insert(index, copy.deepcopy(node[index]))
                    self.assertFalse(valid(mutated), (path, "duplicate", index)); cases += 1
                    mutated = copy.deepcopy(canonical); at(mutated, path)[index] = changed(node[index]) if not isinstance(node[index], (dict, list)) else None
                    self.assertFalse(valid(mutated), (path, "replace", index)); cases += 1
                mutated = copy.deepcopy(canonical); at(mutated, path).append("unknown")
                self.assertFalse(valid(mutated), (path, "append")); cases += 1
                mutated = copy.deepcopy(canonical); at(mutated, path).reverse()
                if len(node) > 1:
                    self.assertFalse(valid(mutated), (path, "reverse")); cases += 1
                for replacement in ({}, "invalid", None):
                    mutated = copy.deepcopy(canonical); at(mutated, parent_path)[leaf] = replacement
                    self.assertFalse(valid(mutated), (path, "replace-list")); cases += 1
            elif not isinstance(node, (dict, list)):
                mutated = copy.deepcopy(canonical); at(mutated, parent_path)[leaf] = changed(node)
                self.assertFalse(valid(mutated), (path, "same-type")); cases += 1
                mutated = copy.deepcopy(canonical); at(mutated, parent_path)[leaf] = []
                self.assertFalse(valid(mutated), (path, "invalid-type")); cases += 1
                if node is not None:
                    mutated = copy.deepcopy(canonical); at(mutated, parent_path)[leaf] = None
                    self.assertFalse(valid(mutated), (path, "null")); cases += 1
        self.assertGreater(cases, 0)

    def test_binding_specific_mutations_and_cross_reference_breaks_are_rejected(self):
        canonical = load_oracle()
        for operation, sections in canonical["spec"]["fieldRules"].items():
            for section, bindings in sections.items():
                for field in list(bindings):
                    for key, replacement in (("scalarRule", "unknown"), ("required", not bindings[field]["required"]), ("nullable", not bindings[field]["nullable"]), ("immutable", not bindings[field]["immutable"]), ("role", "mutated-role")):
                        mutated = copy.deepcopy(canonical); mutated["spec"]["fieldRules"][operation][section][field][key] = replacement
                        self.assertFalse(valid(mutated), (operation, section, field, key))
                    mutated = copy.deepcopy(canonical); del mutated["spec"]["fieldRules"][operation][section][field]
                    self.assertFalse(valid(mutated), (operation, section, field, "remove-binding"))
                    mutated = copy.deepcopy(canonical); mutated["spec"]["fieldRules"][operation][section][field]["unknown"] = True
                    self.assertFalse(valid(mutated), (operation, section, field, "unknown-key"))
        scalar = next(iter(canonical["spec"]["scalarRules"]))
        mutated = copy.deepcopy(canonical); del mutated["spec"]["scalarRules"][scalar]
        self.assertFalse(valid(mutated))
        mutated = copy.deepcopy(canonical); mutated["spec"]["scalarRules"]["unreferenced"] = copy.deepcopy(mutated["spec"]["scalarRules"][scalar])
        self.assertFalse(valid(mutated))


if __name__ == "__main__":
    unittest.main()
