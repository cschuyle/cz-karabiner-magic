"""Automated checks for the Karabiner config.

Run with:

    python3 -m unittest discover -s tests

These tests do NOT exercise Karabiner at runtime (synthetic key events bypass
Karabiner's manipulators, so true end-to-end testing isn't feasible). Instead
they:

  1. Validate that karabiner.json is well-formed and structurally sane.
  2. Resolve each native key-remapping against a model of the Apple
     "Czech - QWERTY" layout and assert it produces the intended character.

Tier 2 catches the bug classes we actually hit: e.g. a rule that claims to
output "~" but is wired to a key combo that the layout maps to "|".
"""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
CONFIG_PATH = os.path.join(REPO_ROOT, "karabiner", "karabiner.json")
LAYOUT_PATH = os.path.join(HERE, "czech_qwerty_layout.json")

OPTION_NAMES = {"option", "left_option", "right_option"}
SHIFT_NAMES = {"shift", "left_shift", "right_shift"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iter_manipulators(config):
    for profile in config.get("profiles", []):
        rules = profile.get("complex_modifications", {}).get("rules", [])
        for rule in rules:
            for manip in rule.get("manipulators", []):
                yield rule, manip


def mandatory_mods(manip):
    mods = manip.get("from", {}).get("modifiers", {}).get("mandatory", [])
    return frozenset(mods)


def level_for_modifiers(modifiers):
    """Map a list of `to` modifiers to a Czech-QWERTY layout level index."""
    mods = set(modifiers or [])
    has_option = bool(mods & OPTION_NAMES)
    has_shift = bool(mods & SHIFT_NAMES)
    return (2 if has_option else 0) + (1 if has_shift else 0)


class ResolveError(Exception):
    pass


def resolve_to_char(to_events, layout_keys):
    """Resolve a single-event `to` list to the character it should produce."""
    if len(to_events) != 1:
        raise ResolveError(
            "expected exactly one `to` event, got %d" % len(to_events)
        )
    event = to_events[0]
    if "shell_command" in event:
        raise ResolveError(
            "`to` is a shell_command (slow paste / not a native key event): %r"
            % event["shell_command"]
        )
    key_code = event.get("key_code")
    if key_code is None:
        raise ResolveError("`to` event has no key_code: %r" % event)
    if key_code not in layout_keys:
        raise ResolveError("key_code %r is not in the layout model" % key_code)
    level = level_for_modifiers(event.get("modifiers", []))
    char = layout_keys[key_code][level]
    if char is None:
        raise ResolveError(
            "key_code %r at level %d is a dead/unmapped key in the layout"
            % (key_code, level)
        )
    return char


# (from key_code, frozenset of mandatory modifiers) -> intended output char.
# These encode the *intent* of each native remapping so the layout model can
# confirm the wiring actually produces it.
EXPECTED_OUTPUTS = {
    ("quote", frozenset()): "'",
    ("quote", frozenset({"shift"})): "!",
    ("semicolon", frozenset()): ";",
    ("semicolon", frozenset({"shift"})): '"',
    ("backslash", frozenset({"shift"})): "`",
    # Shifted number row -> US-style symbols.
    ("1", frozenset({"shift"})): "+",
    ("2", frozenset({"shift"})): "@",
    ("3", frozenset({"shift"})): "#",
    ("4", frozenset({"shift"})): "$",
    ("5", frozenset({"shift"})): "~",
    ("6", frozenset({"shift"})): "^",
    ("7", frozenset({"shift"})): "&",
    ("8", frozenset({"shift"})): "*",
    ("9", frozenset({"shift"})): "{",
    ("0", frozenset({"shift"})): "}",
}


class TestConfigStructure(unittest.TestCase):
    def setUp(self):
        self.config = load_json(CONFIG_PATH)

    def test_config_is_valid_json(self):
        self.assertIsInstance(self.config, dict)

    def test_has_at_least_one_profile_with_rules(self):
        profiles = self.config.get("profiles", [])
        self.assertTrue(profiles, "no profiles defined")
        total_rules = sum(
            len(p.get("complex_modifications", {}).get("rules", []))
            for p in profiles
        )
        self.assertGreater(total_rules, 0, "no complex_modification rules found")

    def test_every_manipulator_has_from_and_to(self):
        for rule, manip in iter_manipulators(self.config):
            desc = rule.get("description", "<no description>")
            self.assertIn("from", manip, "manipulator missing `from` in %r" % desc)
            self.assertIn("to", manip, "manipulator missing `to` in %r" % desc)


class TestLayoutSemantics(unittest.TestCase):
    def setUp(self):
        self.config = load_json(CONFIG_PATH)
        self.layout_keys = load_json(LAYOUT_PATH)["keys"]

    def _find_manipulator(self, key_code, mods):
        matches = [
            manip
            for _, manip in iter_manipulators(self.config)
            if manip.get("from", {}).get("key_code") == key_code
            and mandatory_mods(manip) == mods
        ]
        return matches

    def test_expected_outputs_resolve_correctly(self):
        for (key_code, mods), expected_char in EXPECTED_OUTPUTS.items():
            with self.subTest(key_code=key_code, mods=sorted(mods)):
                matches = self._find_manipulator(key_code, mods)
                self.assertEqual(
                    len(matches),
                    1,
                    "expected exactly one rule for (%s, %s), found %d"
                    % (key_code, sorted(mods), len(matches)),
                )
                try:
                    actual_char = resolve_to_char(matches[0]["to"], self.layout_keys)
                except ResolveError as exc:
                    self.fail(
                        "(%s, %s) intended to output %r but: %s"
                        % (key_code, sorted(mods), expected_char, exc)
                    )
                self.assertEqual(
                    actual_char,
                    expected_char,
                    "(%s, %s) is wired to produce %r but should produce %r"
                    % (key_code, sorted(mods), actual_char, expected_char),
                )

    def test_expected_keys_present_in_layout_model(self):
        for (key_code, _mods) in EXPECTED_OUTPUTS:
            self.assertIn(key_code, self.layout_keys)


if __name__ == "__main__":
    unittest.main()
