<h1 align="center">Russian language pack for Orca</h1>

<p align="center">
  <a href="https://github.com/smwbev/orca-russian/releases"><img src="https://img.shields.io/badge/version-5.1.178-08C?style=flat" alt="Package version 5.1.178" /></a>
  <img src="https://img.shields.io/badge/coverage-99.9%25-08C?style=flat" alt="99.9 percent of the strings in use that a language pack may translate" />
  <img src="https://img.shields.io/badge/strings-16%20476-08C?style=flat" alt="16,476 translated strings" />
  <img src="https://img.shields.io/badge/Orca-%E2%89%A5%201.4.169-4493F8?style=flat" alt="Requires Orca 1.4.169 or newer" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-08C?style=flat" alt="MIT License" /></a>
</p>

<p align="center">
  <sub><a href="docs/readme/README.ru.md">Русский</a></sub>
</p>

<p align="center">
  <strong>A complete Russian translation of the <a href="https://github.com/stablyai/orca">Orca</a> interface.</strong><br/>
  16,476 strings — menus, settings, terminal, editor, GitHub, GitLab, Linear, Jira, mobile, and onboarding.
</p>

> [!IMPORTANT]
> **Orca now has Russian built in.** Since Orca 1.4.244, choose **Settings → Appearance → Language → Русский**; Orca also picks it on its own when the system language is Russian ([stablyai/orca#34717](https://github.com/stablyai/orca/pull/34717)).
> This pack is no longer maintained. v5.1.178, made for Orca 1.4.244, is its last release. While the pack is selected, strings Orca adds later show in English, so switch to the built-in language and remove the pack in **Settings → Plugins**.

---

## Install

### Option 1 — via the marketplace (recommended)

A marketplace install updates in place: **Check for update** on the pack's card fetches the newest release.

1. **Settings** → **Plugins** → turn on **Plugin system**.
2. Click **Manage sources**. Paste the URL into **Git URL**, leave **Git ref** at `main`, and click **Add source**:

   ```
   https://github.com/smwbev/orca-plugins.git
   ```

3. In the **All** tab, find the **Russian** card from `smwbev`, click **Install**, and confirm with **Install plugin**.
4. Orca opens **Review plugin**. The pack is declarative content with no plugin code; click **Enable plugin**. The language is not offered until you do.
5. **Settings** → **Appearance** → **Language** → select `ru-RU — smwbev.russian`.

### Option 2 — directly from a Git URL

1. **Settings** → **Plugins** → **Install plugin** → **Git URL** tab.
2. Paste the repository URL **with an explicit `#ref`** — Orca refuses the install without one, so that every install is pinned:

   ```
   https://github.com/smwbev/orca-russian.git#v5.1.178
   ```

   Any tag or commit works after `#`. There is no separate ref field in this dialog — the ref is part of the URL.

3. In **Review plugin**, click **Enable plugin**.
4. **Settings** → **Appearance** → **Language** → `ru-RU — smwbev.russian`.

### Option 3 — local development folder

1. Clone the repository into a permanent directory:

   ```bash
   git clone https://github.com/smwbev/orca-russian.git
   ```

2. **Settings** → **Plugins** → **Development** → enter the full path to the folder and click **Add path**.
3. Review and enable the plugin when Orca asks, then select the language. Restart Orca if the pack does not show up.

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

189 keys of the Orca v1.4.244 catalog stay in English. None of it is missing work:

- **180 strings** — plugin consent and trust copy. The engine protects the `auto.components.settings.plugin*` namespace with a case-insensitive check, so a pack cannot rewrite a consent dialog, a provenance badge, a safety status, or a destructive confirmation. If a language pack overrides even one of those keys, Orca rejects **the entire pack** and the language never loads.
- **9 strings** — identical in Russian (`SHA-256`, `· SSH`, `WSL ·`, a sample share URL, `{{name}} +{{count}}`, `{{count}} × {{label}}`).

The list shrinks as Orca merges the fixes we send:

- **34 strings** left it in [PR #11826](https://github.com/stablyai/orca/pull/11826) — status labels in Settings and Stats were built from literals inside helper functions and never reached the catalog at all. Translated since v5.1.0.
- **34 more** left it in [PR #12455](https://github.com/stablyai/orca/pull/12455), which narrowed the namespace rule so that section titles, empty states, `Refresh` and the local development form — none of which carry a trust decision — became translatable. Shipped in Orca v1.4.169, translated since pack v5.1.7. An older Orca build rejects a catalog that carries them, so the manifest declares `engines.orca >=1.4.169` and such a build refuses the install with a message naming the version it needs.

Any key missing from the pack falls back to English automatically — that is the engine's normal behaviour, and the app keeps working.

---

## Updating

**Marketplace:** in **Settings** → **Plugins**, click **Check for update** on the pack's card, then **Update plugin**.

**Git URL:** reinstall the plugin pinned to the newer tag.

Version history: [releases](https://github.com/smwbev/orca-russian/releases) from v5.1.157 on, [tags](https://github.com/smwbev/orca-russian/tags) for everything earlier. Versions follow `vX.Y.Z`; a major bump marks the completion of a large translation stage.

---

## How the pack is built

```
orca-plugin.json        manifest: identity, version, catalog path
locales/ru-RU.json      translation catalog, 16,476 strings and 331 extra plural forms
GLOSSARY.md             glossary: rules and consistent terminology (Russian)
tools/                  the build, the release check and a pack audit — see tools/README.md
```

Orca loads language packs under a synthetic language code, which is why the picker shows `ru-RU — smwbev.russian`. Catalog keys mirror the English source at `src/renderer/src/i18n/locales/en.json`; anything absent from the Russian file is served from English.

Russian needs more plural forms than English has. Since Orca v1.4.243 a pack's plurals follow the locale the pack declares ([stablyai/orca#12505](https://github.com/stablyai/orca/pull/12505)), so Russian gets its own forms: «сохранена 21 ветка», «сохранены 2 ветки», «сохранено 5 веток». Where the pack has no form for a count, Orca shows its `_other` text, so that text is still worded to read correctly for any number: «сохранено веток: 5».

The 331 extra entries are the forms English lacks: `_few` and `_many` for 71 plural families, and `_one`, `_few` and `_many` for 63 strings that Orca calls with a count but ships as a single text. They render since Orca v1.4.243.

Every release is rebuilt with [`tools/build.py`](tools/build.py) and validated against the rules of the latest Orca release, not of `main`:

| Limit | Cap | Current |
|---|---|---|
| Catalog nodes | 20,000 | 18,958 |
| Nesting depth | 16 | 12 |
| String length | 8,192 chars | within limit |
| File size | 5 MB | ~1.6 MB |

[`tools/audit-pack.py`](tools/audit-pack.py) runs the same checks on any language pack, not only this one: whether the engine would accept the catalog, what a release left untranslated, and which keys it no longer defines.

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

Requires **Orca 1.4.169 or newer**. Pluggable language packs appeared in 1.4.160, but this pack translates 34 plugin-settings strings that only 1.4.169 and later let a pack override, and an older build rejects the whole catalog over a single one of them. The manifest declares the minimum, so an older Orca refuses the install and names the version it needs instead of silently staying in English.

**Fixed in Orca 1.4.229: the roadmap crash.** In Orca 1.4.198 – 1.4.227, opening a GitHub Project roadmap with any language pack active crashed the Tasks page: the roadmap handed the pack's internal resource name to the date formatter, which rejected it. Orca 1.4.229 includes the fix ([#26860](https://github.com/stablyai/orca/pull/26860)); before it, the fix shipped only in 1.4.225 and 1.4.226, both withdrawn, and the hotfix 1.4.227 did not have it. If you are on an earlier version, update Orca.

The pack ships text data only: it executes no code, requests no permissions, and has no access to your files, repositories, or credentials. The scripts in `tools/` maintain the catalog; the manifest declares no entry point, so Orca never runs them.

---

## License

Released under the [MIT License](LICENSE) — the same license Orca itself uses.

The English interface catalog this pack derives from is Copyright (c) Stably AI and MIT-licensed. Catalog keys, structure, and a small number of verbatim strings — CSS blocks, command examples, internal identifiers — originate there and remain under its terms; see [NOTICE](NOTICE) for details.
