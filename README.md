<h1 align="center">Russian language pack for Orca</h1>

<p align="center">
  <a href="https://github.com/smwbev/orca-russian/releases"><img src="https://img.shields.io/badge/version-5.1.63-08C?style=flat" alt="Package version 5.1.63" /></a>
  <img src="https://img.shields.io/badge/coverage-99.3%25-08C?style=flat" alt="99.3 percent of the interface catalog translated" />
  <img src="https://img.shields.io/badge/strings-12%20948-08C?style=flat" alt="12,948 translated strings" />
  <img src="https://img.shields.io/badge/Orca-%E2%89%A5%201.4.0-4493F8?style=flat" alt="Requires Orca 1.4.0 or newer" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-08C?style=flat" alt="MIT License" /></a>
</p>

<p align="center">
  <sub><a href="docs/readme/README.ru.md">Русский</a></sub>
</p>

<p align="center">
  <strong>A complete Russian translation of the <a href="https://github.com/stablyai/orca">Orca</a> interface.</strong><br/>
  12,948 strings — menus, settings, terminal, editor, GitHub, GitLab, Linear, Jira, mobile, and onboarding.
</p>

---

## Install

### Option 1 — via the marketplace (recommended)

The marketplace tracks updates for you: when a new translation release ships, Orca offers to install it.

1. **Settings** → **Plugins** → enable the plugin system.
2. Open **Marketplace sources** → **Add source**.
3. Paste the URL and confirm:

   ```
   https://github.com/smwbev/orca-plugins.git
   ```

4. In the **All** tab, find **Русский** and click **Install**.
5. **Settings** → **Appearance** → **Language** → select `ru-RU — smwbev.russian`.

### Option 2 — directly from a Git URL

1. **Settings** → **Plugins** → **Install plugin** → **Git URL** tab.
2. Paste the repository URL **with an explicit `#ref`** — Orca refuses the install without one, so that every install is pinned:

   ```
   https://github.com/smwbev/orca-russian.git#v5.1.63
   ```

   Any tag or commit works after `#`. There is no separate ref field in this dialog — the ref is part of the URL.

3. **Settings** → **Appearance** → **Language** → `ru-RU — smwbev.russian`.

### Option 3 — local development folder

1. Clone the repository into a permanent directory:

   ```bash
   git clone https://github.com/smwbev/orca-russian.git
   ```

2. **Settings** → **Plugins** → add the full path to **development plugin paths** (`devPluginPaths`).
3. Restart Orca and select the language.

---

## Coverage

| Area | Status |
|---|---|
| App shell: menus, tray, status bar, sidebars, tabs | ✅ |
| All settings: appearance, terminal, accounts, repositories, Git, agents, integrations, privacy, shortcuts | ✅ |
| Working surfaces: editor, diff, palettes, tasks, automations | ✅ |
| Integrations: GitHub, GitLab, Linear, Jira | ✅ |
| Mobile mode, phone pairing, emulator | ✅ |
| Onboarding and the feature wall | ✅ |
| Plugins section in settings | ⚠️ frame translated, consent copy stays in English |

### Why some strings stay in English

303 catalog keys stay in English. None of it is missing work:

- **180 strings** — plugin consent and trust copy. The engine protects the `auto.components.settings.plugin*` namespace with a case-insensitive check, so a pack cannot rewrite a consent dialog, a provenance badge, a safety status, or a destructive confirmation. If a language pack overrides even one of those keys, Orca rejects **the entire pack** and the language never loads.
- **2 strings** — feature-wall CSS animations of 9,691 and 9,965 characters against a hard limit of 8,192 characters per string.
- **1 string** — another CSS block with nothing to translate.
- **112 keys** — orphans left in the English catalog after the skill-sharing feature was reverted and relanded; no component reads them, so translating them would only add weight.
- **8 strings** — identical in Russian (`SHA-256`, `· SSH`, `WSL ·`, a sample share URL, `{{name}} +{{count}}`), or split into fragments that the component pluralises with a hard-coded English `s`.

The list shrinks as Orca merges the fixes we send:

- **34 strings** left it in [PR #11826](https://github.com/stablyai/orca/pull/11826) — status labels in Settings and Stats were built from literals inside helper functions and never reached the catalog at all. Translated since v5.1.0.
- **34 more** left it in [PR #12455](https://github.com/stablyai/orca/pull/12455), which narrowed the namespace rule so that section titles, empty states, `Refresh` and the local development form — none of which carry a trust decision — became translatable. Shipped in Orca v1.4.169, translated since pack v5.1.7. On older Orca builds the pack drops those keys automatically, so it keeps loading there.

Any key missing from the pack falls back to English automatically — that is the engine's normal behaviour, and the app keeps working.

---

## Updating

**Marketplace:** Orca notifies you about a new version — click **Update**.

**Git URL:** reinstall the plugin pinned to the newer tag.

Version history lives in [releases](https://github.com/smwbev/orca-russian/releases). Releases follow `vX.Y.Z`; a major bump marks the completion of a large translation stage.

---

## How the pack is built

```
orca-plugin.json        manifest: identity, version, catalog path
locales/ru-RU.json      translation catalog, 12,948 strings
GLOSSARY.md             glossary: rules and consistent terminology (Russian)
```

Orca loads language packs under a synthetic language code, which is why the picker shows `ru-RU — smwbev.russian`. Catalog keys mirror the English source at `src/renderer/src/i18n/locales/en.json`; anything absent from the Russian file is served from English.

Every release is validated against the engine limits:

| Limit | Cap | Current |
|---|---|---|
| Catalog nodes | 20,000 | 13,838 |
| Nesting depth | 16 | 12 |
| String length | 8,192 chars | within limit |
| File size | 5 MB | ~1 MB |

---

## Terminology

The translation follows a single glossary — [GLOSSARY.md](GLOSSARY.md) (written in Russian). Beyond term mappings it fixes the rules: impersonal address, verbatim placeholders, consistent «ё», typographic quotes and ellipses, and how to separate look-alike concepts.

Git commands, product names, and internal identifiers deliberately stay in Latin script.

---

## Reporting a translation issue

Open an [issue](https://github.com/smwbev/orca-russian/issues) with:

1. The current wording and what it should say instead.
2. Where it appears — the interface section or a screenshot.

Terminology changes are applied catalog-wide rather than to a single string, so that the glossary stays authoritative.

---

## Compatibility

Requires **Orca 1.4.0 or newer** — earlier versions do not support pluggable language packs.

The pack ships text data only: it executes no code, requests no permissions, and has no access to your files, repositories, or credentials.

---

## License

Released under the [MIT License](LICENSE) — the same license Orca itself uses.

The English interface catalog this pack derives from is Copyright (c) Stably AI and MIT-licensed. Catalog keys, structure, and a small number of verbatim strings — CSS blocks, command examples, internal identifiers — originate there and remain under its terms; see [NOTICE](NOTICE) for details.
