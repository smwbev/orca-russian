# Tools

The scripts that build and check this pack. Orca does not load them: the manifest declares no entry point, and a language pack is data only.

| Script | What it does |
|---|---|
| [`audit-pack.py`](audit-pack.py) | Audits any Orca language pack against one Orca release: whether the engine would accept the catalog, coverage, untranslated and stale keys, placeholder drift. |
| [`build.py`](build.py) | Builds `locales/ru-RU.json` from translation blocks and validates it against the rules of the latest stable Orca release. |
| [`release-check.py`](release-check.py) | Checks that the version and every count agree across the manifest, both READMEs and the glossary. Run before tagging. |

They need `python3` 3.8 or newer and an authenticated [`gh`](https://cli.github.com/). Run them from the repository root.

`audit-pack.py` is written in English because it is meant for any pack author. `build.py` and `release-check.py` print and are commented in Russian, like the glossary: they are this pack's own workflow.

## Auditing a pack

```bash
python3 tools/audit-pack.py                      # this pack, latest stable Orca release
python3 tools/audit-pack.py --release v1.4.224   # a specific release
python3 tools/audit-pack.py path/to/another-pack # any directory with an orca-plugin.json
python3 tools/audit-pack.py --list               # every missing and stale key
python3 tools/audit-pack.py --release main       # preview a rule that has not shipped yet
```

```
Orca v1.4.242: 17187 catalog keys, 17007 a pack may translate (180 protected, 0 over 8192 characters, 34 allow-listed, 0 components protected outright).

smwbev.russian v5.1.176 — ru-RU, locales/ru-RU.json, engines >=1.4.169
  engine verdict: ACCEPTED
  size: 19187/20000 entries, depth 12/16, 1618808 bytes
  coverage: 16874/17007 = 99.22 % of what a pack may translate; 133 missing
  stale keys the release does not define: 0
  extra plural forms: 217 — `_few` and `_many` stay unreachable until stablyai/orca#12505
  identical to English: 1087
  placeholders the English source does not have: 0
    missing: auto.components.automations.externalScope.unknownManager
    missing: auto.components.settings.shareSkills.refreshLinks
    missing: auto.components.skills.SkillBundleInstallFlow.01c5a13e04
    missing: auto.components.skills.SkillBundleInstallFlow.01c5a13e05
    missing: auto.components.skills.SkillBundleInstallOutcome.01c5a12e05
    … 128 more missing (use --list)
```

The exit status is 1 when the engine would reject a pack, so the script can gate a release.

The verdict mirrors the checks Orca runs on a language pack at install time:

- **Protected paths.** Everything under `auto.components.settings.plugin*` is consent and trust copy, except the paths listed in `plugin-translatable-chrome.ts`. Whole components the engine module lists in `PROTECTED_TRANSLATION_COMPONENTS` are protected with no exceptions (the native chat approval card and two plugin trust labels, from [stablyai/orca#33069](https://github.com/stablyai/orca/pull/33069), not in a release yet). One protected key and Orca rejects the whole catalog without a message; the interface just stays English.
- **Limits.** The entry limit is read from the release's engine module (20,000 up to v1.4.242), plus depth 16, 8,192 characters per value, 5 MB per file.
- **Rules the script does not know.** If the release's engine module declares a protection rule this script does not model, the audit stops with an error instead of printing a verdict.
- **Unsafe keys.** Empty keys, keys with a dot or a control character, `__proto__`, `prototype`, `constructor`.

### Why the rules are read from the release, not from `main`

A pack is installed on a release. A rule that has only reached `main` applies to nobody yet.

Pack v5.1.4 learned this the hard way: it shipped 34 strings the allow-list had just opened up on `main`, the current release still protected them, and Russian stopped loading for everyone on it. The same reasoning sets `engines.orca` to `>=1.4.169`, the first release that carries the allow-list.

## Building

```bash
python3 tools/build.py
```

The committed catalog is the base. Translation blocks are laid over it: flat JSON files named `wave*-ru-part*.json` in the working directory `.i18n-work/` (not tracked; set `ORCA_RU_WORK` for another path), each mapping a dotted key to its translation. With no blocks the build re-validates the catalog and writes it back unchanged.

The build then:

- drops a key that neither the latest release nor `main` defines, and fails if such a key came from a block;
- fails on a protected key, a placeholder the English source does not have, or any engine limit;
- accepts a plural form English lacks (`_few` and `_many` of a plural family; `_one`, `_few` and `_many` of a string Orca calls with a count) only while the string it extends is alive in Orca's catalog and translated in the pack;
- warns about a value with no Cyrillic, a missing «ё», or a dropped placeholder, which is usually the English plural `s`.

Nothing is written when a check fails.

## Before tagging

```bash
python3 tools/release-check.py
```

A published tag never moves, so the only protection against a stale number is a check before the tag. The script compares the manifest version and the catalog's string count with every place the documentation states them, and checks that the "stay in English" total equals the sum of its own breakdown.
