<h1 align="center">Russian language pack for Orca</h1>

<p align="center">
  <a href="https://github.com/smwbev/orca-russian/releases"><img src="https://img.shields.io/badge/version-5.0.1-08C?style=flat" alt="Package version 5.0.1" /></a>
  <img src="https://img.shields.io/badge/coverage-98.2%25-08C?style=flat" alt="98.2 percent of the interface catalog translated" />
  <img src="https://img.shields.io/badge/strings-11%20613-08C?style=flat" alt="11,613 translated strings" />
  <img src="https://img.shields.io/badge/Orca-%E2%89%A5%201.4.0-4493F8?style=flat" alt="Requires Orca 1.4.0 or newer" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-08C?style=flat" alt="MIT License" /></a>
</p>

<p align="center">
  <sub><a href="README.md">Русский</a></sub>
</p>

<p align="center">
  <strong>A complete Russian translation of the <a href="https://github.com/stablyai/orca">Orca</a> interface.</strong><br/>
  11,613 strings — menus, settings, terminal, editor, GitHub, GitLab, Linear, Jira, mobile, and onboarding.
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
2. Paste the repository URL:

   ```
   https://github.com/smwbev/orca-russian.git
   ```

3. Pin a release tag (for example `v5.0.1`), or leave `main` for the latest build.
4. **Settings** → **Appearance** → **Language** → `ru-RU — smwbev.russian`.

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
| Plugins section in settings | ⛔ stays in English |

### Why some strings stay in English

217 strings cannot be translated. This is an Orca constraint, not missing work:

- **214 strings** — the plugin settings section. The engine protects the `auto.components.settings.plugin*` namespace with a case-insensitive check, so `PluginSettingsRow` and `PluginsSettingsSection` are covered too. If a language pack overrides even one of those keys, Orca rejects **the entire pack** and the language never loads.
- **2 strings** — feature-wall CSS animations of 9,691 and 9,965 characters against a hard limit of 8,192 characters per string.
- **1 string** — another CSS block with nothing to translate.

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
locales/ru-RU.json      translation catalog, 11,613 strings
GLOSSARY.md             glossary: rules and consistent terminology (Russian)
```

Orca loads language packs under a synthetic language code, which is why the picker shows `ru-RU — smwbev.russian`. Catalog keys mirror the English source at `src/renderer/src/i18n/locales/en.json`; anything absent from the Russian file is served from English.

Every release is validated against the engine limits:

| Limit | Cap | Current |
|---|---|---|
| Catalog nodes | 20,000 | 13,010 |
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

The English interface catalog this pack derives from is Copyright (c) Stably AI and MIT-licensed. Catalog keys, structure, and a small number of verbatim strings — CSS blocks, command examples, internal identifiers — originate there and remain under its terms.
