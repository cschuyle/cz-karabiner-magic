# cz-karabiner-magic

A [Karabiner-Elements](https://karabiner-elements.pqrs.org/) config for a
Czech-keycap MacBook (a "Neo" I bought in Prague in June 2026), tweaked so it
behaves close to the US layout my muscle memory expects — while still mostly
respecting what's actually printed on the keys.

I wanted to be functional fast, so the changes are deliberately minimal and
pragmatic rather than a "proper" custom keyboard layout.

## Requirements

- **macOS** with [Karabiner-Elements](https://karabiner-elements.pqrs.org/)
  installed (built/tested against **v16.0.0**).
- Input Source set to **Czech – QWERTY** in System Settings → Keyboard →
  Input Sources.
- **Only that one input source installed.** Several mappings here depend on the
  active layout being Czech QWERTY; extra input sources can change what a key
  produces and break things.

## What the config does

- The MacOS **Czech QWERTY** input source variant already swaps `Y` and `Z` into their US
  positions, so no remap is needed. This makes the keycaps lie, which I find OK.
- **Unshifted number row** - press a number key to get the digit; press `⇧` to get what would otherwise be got by using `⌥`, which is more or less what US keyboards do `⌥` : `@` `#` `$` `~` `^` `&` `*` `{` `}`
- **A few extra symbol fixes** — `⇧`-`1` → `+`, `=` / `%` on the equals key,
  and `⇧`-`<umlaut-combinator>` → backtick (`` ` ``).
- **Umlaut dead-key combiner → `↩`**, because the physical `↩`
  key is too skinny for my fingers. Yes, I sacrified the umlaut.
- **`§` (section) → `'`** and **`ů` → `;`** (with `"` on `⇧`-`ů`), so common
  programmer punctuation doesn't require `⌥` gymnastics.

## The dead-key gotcha (why some mappings look weird)

On the Czech QWERTY layout several physical keys are **dead keys** (e.g. the
quote key is an acute-accent combiner), so naively remapping a key to
`key_code: quote` produces an accent, not the character you want.

So instead of remapping to the bare key, the config emits **native key events
that target the correct level of the Czech QWERTY layout**. For example, a
literal apostrophe is `⌥` + `quote` on this layout, so the rule emits exactly
that — no dead key, no latency.

If you're adapting this for a different layout, the key insight is: find which
`key_code` + modifier combination already produces the character you want under
your active macOS layout, and map *to* that.

## Install

This repo's `karabiner/` directory **is** a Karabiner config directory. The
intended setup is to symlink Karabiner's config location to it, so editing the
repo updates the live config directly (Karabiner reloads on file change).

> [!WARNING]
> This replaces your existing Karabiner configuration. Back it up first.

```sh
# 1. Back up whatever you have now (if anything).
mv ~/.config/karabiner ~/.config/karabiner.backup-$(date +%Y%m%d) 2>/dev/null || true

# 2. Point Karabiner at this repo's config dir.
git clone https://github.com/<you>/cz-karabiner-magic.git
ln -s "$PWD/cz-karabiner-magic/karabiner" ~/.config/karabiner
```

Then open Karabiner-Elements and confirm the profile loaded. Because the symlink
points at the repo, any commit you pull or edit you make takes effect live.

## macOS keyboard-shortcut tweaks (outside Karabiner)

Useful system shortcuts you can also configure manually in
**System Settings → Keyboard → Keyboard Shortcuts**, because the stock Czech
layout moves keys around:

- **Move focus to next window** ("go to next window") → set it to `⌥` + the
  `´` / `ˇ` dead-key (acute unshifted, háček/caron when shifted — the key just
  to the right of `%=`).

## Tests

The remappings are validated without needing Karabiner running. (True
end-to-end testing isn't feasible: synthetic key events bypass Karabiner's
manipulators, and the output depends on the live input source.)

Instead, the tests model the Apple "Czech – QWERTY" layout and assert that each
native remapping is wired to the `key_code` + modifier combo that actually
produces the intended character. This catches mistakes like a rule that *claims*
to output `~` but is wired to a combo the layout maps to `|`.

```sh
python3 -m unittest discover -s tests -v
```

- `tests/czech_qwerty_layout.json` — model of the layout (each key's output at
  the base / Shift / Option / Option+Shift levels).
- `tests/test_karabiner_config.py` — JSON/structure validation plus the
  layout-semantic checks. Add a row to `EXPECTED_OUTPUTS` to cover another key.
