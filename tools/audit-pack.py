#!/usr/bin/env python3
"""Audit an Orca language pack against one Orca release.

    python3 tools/audit-pack.py                     # this pack, latest stable Orca release
    python3 tools/audit-pack.py --release v1.4.224  # a specific release
    python3 tools/audit-pack.py path/to/other-pack  # any pack with an orca-plugin.json
    python3 tools/audit-pack.py --en en.json --chrome plugin-translatable-chrome.ts \
        --artifact plugin-language-pack-artifact.ts                                  # offline

It answers the questions a pack author has after every Orca release:

- Will the engine accept the catalog? A single protected key, an over-long value or an
  unsafe key makes Orca reject the whole pack, and the UI silently stays English.
- Which release strings are still untranslated, and which pack keys does the release
  no longer define?
- Do placeholders match the English source?

The rules are read from the release tag, not from Orca's main branch: a pack is installed
on a release, and a rule that has only reached main does not apply to anyone yet. That
includes the engine module itself: whole components it protects outright (the native chat
approval card, since stablyai/orca#33069) and its entry limit. A protection rule this script
does not know stops the audit instead of passing it.
Needs python3 and, unless --en/--chrome are given, an authenticated `gh`.
Exit status is 1 when the engine would reject at least one audited pack.
"""
import argparse, base64, json, os, re, subprocess, sys

REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
CHROME_PATH = 'src/shared/plugins/plugin-translatable-chrome.ts'
# The engine module moved into artifacts/ with the plugins-v2 work; releases up to v1.4.242 have it here.
ARTIFACT_PATHS = ['src/shared/plugins/artifacts/plugin-language-pack-artifact.ts',
                  'src/shared/plugins/plugin-language-pack-artifact.ts']
KNOWN_RULES = {'PROTECTED_TRANSLATION_ROOT': "'auto.components.settings.'",
               'PROTECTED_TRANSLATION_MODULE': '/^plugin/i',
               'PROTECTED_TRANSLATION_COMPONENTS': None}
PROTECTED_ROOT = 'auto.components.settings.'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}
MAX_ENTRIES, MAX_DEPTH, MAX_VALUE, MAX_BYTES = 20_000, 16, 8192, 5 * 1024 * 1024
PLURAL = re.compile(r'_(zero|one|two|few|many|other)$')


def gh(*args):
    result = subprocess.run(['gh', *args], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f'gh {" ".join(args[:2])} failed: {result.stderr.strip() or "empty response"}')
    return result.stdout


def gh_optional(*args):
    """Like gh(), but a missing file is None: the engine module has lived at two paths."""
    result = subprocess.run(['gh', *args], capture_output=True, text=True)
    if result.returncode != 0 and 'HTTP 404' in result.stderr:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(f'gh {" ".join(args[:2])} failed: {result.stderr.strip() or "empty response"}')
    return result.stdout


def flatten(tree, prefix=''):
    out = {}
    for key, value in tree.items():
        path = f'{prefix}.{key}' if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def shape(tree, depth=0):
    """Entries, deepest level and unsafe keys, counted the way the engine walks a catalog."""
    entries, deepest, unsafe = 0, depth, []
    for key, value in tree.items():
        entries += 1
        if not key or len(key) > 128 or key in DANGEROUS or '.' in key or any(ord(c) <= 31 for c in key):
            unsafe.append(key)
        if isinstance(value, dict):
            child_entries, child_depth, child_unsafe = shape(value, depth + 1)
            entries += child_entries
            deepest = max(deepest, child_depth)
            unsafe += child_unsafe
    return entries, deepest, unsafe


def placeholders(text):
    return set(re.findall(r'\{\{[^}]*\}\}', text))


parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
parser.add_argument('packs', nargs='*', help='pack directories (default: the repository this script lives in)')
parser.add_argument('--release', help='Orca release tag (default: latest stable)')
parser.add_argument('--en', help='local en.json of the release, instead of fetching it')
parser.add_argument('--chrome', help='local plugin-translatable-chrome.ts of the release')
parser.add_argument('--artifact', help='local plugin-language-pack-artifact.ts of the release')
parser.add_argument('--list', action='store_true', help='print every missing and stale key, not just a sample')
args = parser.parse_args()

release = args.release
if not release and not (args.en and args.chrome):
    release = gh('release', 'view', '--repo', REPO, '--json', 'tagName', '--jq', '.tagName').strip()
if args.en:
    english = flatten(json.load(open(args.en, encoding='utf-8')))
else:
    # The raw media type matters: for a file over 1 MiB the contents API returns an empty
    # `.content` without an error. en.json is within a few percent of that size, and the
    # ko and fr catalogs are already past it.
    english = flatten(json.loads(gh('api', '-H', 'Accept: application/vnd.github.raw+json',
                                    f'repos/{REPO}/contents/{EN_PATH}?ref={release}')))
if args.chrome:
    chrome_source = open(args.chrome, encoding='utf-8').read()
else:
    chrome_source = base64.b64decode(gh('api', f'repos/{REPO}/contents/{CHROME_PATH}?ref={release}',
                                        '--jq', '.content')).decode('utf-8')
allowed_chrome = set(re.findall(r"'(auto\.components\.settings\.[^']+)'", chrome_source))

if args.artifact:
    artifact_source = open(args.artifact, encoding='utf-8').read()
elif release:
    artifact_source = next((s for s in (gh_optional('api', '-H', 'Accept: application/vnd.github.raw+json',
                                                    f'repos/{REPO}/contents/{p}?ref={release}')
                                        for p in ARTIFACT_PATHS) if s), None)
    if artifact_source is None:
        sys.exit(f'the engine module is at neither {" nor ".join(ARTIFACT_PATHS)} in {release}; '
                 'find where it moved and add the path to ARTIFACT_PATHS')
else:
    artifact_source = None
    print('No --artifact: whole protected components and the release entry limit are not checked.\n')
protected_components = []
if artifact_source:
    # A rule this script does not model would let it print ACCEPTED for a pack the engine rejects,
    # which is how a whole pack silently falls back to English. Stop instead.
    rules = dict(re.findall(r'\bconst (PROTECTED_[A-Z_]+)\s*=\s*([^\n]+)', artifact_source))
    unknown = sorted(set(rules) - set(KNOWN_RULES))
    changed = sorted(k for k, v in KNOWN_RULES.items() if v is not None and k in rules and rules[k].strip() != v)
    if unknown or changed:
        sys.exit(f'the engine in {release or args.artifact} has protection rules this script does not model '
                 f'({", ".join(unknown + changed)}); compare isProtectedPluginTranslationPath with protected() '
                 'here before trusting a verdict')
    listed = re.search(r'PROTECTED_TRANSLATION_COMPONENTS\s*=\s*\[(.*?)\]', artifact_source, re.S)
    protected_components = re.findall(r"'([^']+)'", listed.group(1)) if listed else []
    limit = re.search(r'PLUGIN_LANGUAGE_CATALOG_MAX_ENTRIES\s*=\s*([\d_]+)', artifact_source)
    if limit:
        MAX_ENTRIES = int(limit.group(1).replace('_', ''))


def protected(path):
    """The engine's rule: settings.plugin* is consent and trust copy, minus an explicit allow-list,
    and whole components no pack may relabel, with no allow-list."""
    if any(path == c or path.startswith(c + '.') for c in protected_components):
        return True
    if not path.startswith(PROTECTED_ROOT) or path in allowed_chrome:
        return False
    return path[len(PROTECTED_ROOT):].lower().startswith('plugin')


translatable = {k for k, v in english.items() if not protected(k) and len(v) <= MAX_VALUE}
print(f'Orca {release or "(local catalog)"}: {len(english)} catalog keys, {len(translatable)} a pack may translate '
      f'({sum(1 for k in english if protected(k))} protected, '
      f'{sum(1 for v in english.values() if len(v) > MAX_VALUE)} over {MAX_VALUE} characters, '
      f'{len(allowed_chrome)} allow-listed, {len(protected_components)} components protected outright).\n')

rejected = False
default_pack = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for root in args.packs or [default_pack]:
    manifest = json.load(open(os.path.join(root, 'orca-plugin.json'), encoding='utf-8'))
    for pack in manifest['contributes']['languagePacks']:
        path = os.path.join(root, pack['path'])
        tree = json.load(open(path, encoding='utf-8'))
        catalog = flatten(tree)
        entries, depth, unsafe = shape(tree)
        size = os.path.getsize(path)

        reasons = []
        blocked = sorted(k for k in catalog if protected(k))
        too_long = sorted(k for k, v in catalog.items() if isinstance(v, str) and len(v) > MAX_VALUE)
        not_text = sorted(k for k, v in catalog.items() if not isinstance(v, str))
        if blocked: reasons.append(f'{len(blocked)} protected keys, first: {blocked[0]}')
        if too_long: reasons.append(f'{len(too_long)} values over {MAX_VALUE} characters, first: {too_long[0]}')
        if not_text: reasons.append(f'{len(not_text)} values that are not strings, first: {not_text[0]}')
        if unsafe: reasons.append(f'{len(unsafe)} unsafe keys, first: {unsafe[0]!r}')
        if entries > MAX_ENTRIES: reasons.append(f'{entries} entries, limit {MAX_ENTRIES}')
        if depth > MAX_DEPTH: reasons.append(f'depth {depth}, limit {MAX_DEPTH}')
        if size > MAX_BYTES: reasons.append(f'{size} bytes, limit {MAX_BYTES}')
        rejected = rejected or bool(reasons)

        text = {k: v for k, v in catalog.items() if isinstance(v, str)}
        covered = [k for k in text if k in translatable]
        missing = sorted(translatable - set(text))
        # A plural form the language needs and English lacks is not stale while its family
        # lives: English has the same base with `_one`/`_other`, or the bare base key that a
        # `count` call falls back to.
        def family(key):
            base = PLURAL.sub('', key)
            return [english[k] for k in (base + '_other', base + '_one', base) if k in english]

        extra_plural = sorted(k for k in text if k not in english and PLURAL.search(k) and family(k))
        stale = sorted(k for k in text if k not in english and k not in extra_plural)
        same = [k for k in covered if text[k] == english[k]]
        def known_placeholders(key):
            sources = [english[key]] if key in english else family(key)
            found = set().union(*map(placeholders, sources)) if sources else set()
            # A family's forms share one `count` call: `_one` may show the count even where
            # English words its singular without it ("Reopen terminal").
            if key in english and PLURAL.search(key) and '{{count}}' in english.get(PLURAL.sub('', key) + '_other', ''):
                found.add('{{count}}')
            return sources, found

        surplus = sorted(k for k in text
                         if (known := known_placeholders(k))[0] and placeholders(text[k]) - known[1])

        print(f'{manifest.get("publisher")}.{manifest.get("id")} v{manifest.get("version")} — '
              f'{pack.get("locale")}, {pack["path"]}, engines {manifest.get("engines", {}).get("orca")}')
        print(f'  engine verdict: {"ACCEPTED" if not reasons else "REJECTED — " + "; ".join(reasons)}')
        print(f'  size: {entries}/{MAX_ENTRIES} entries, depth {depth}/{MAX_DEPTH}, {size} bytes')
        print(f'  coverage: {len(covered)}/{len(translatable)} = {100 * len(covered) / len(translatable):.2f} % '
              f'of what a pack may translate; {len(missing)} missing')
        print(f'  stale keys the release does not define: {len(stale)}')
        print(f'  extra plural forms: {len(extra_plural)}'
              + (' — `_few` and `_many` stay unreachable until stablyai/orca#12505' if extra_plural else ''))
        print(f'  identical to English: {len(same)}')
        print(f'  placeholders the English source does not have: {len(surplus)}')
        for label, keys in (('missing', missing), ('stale', stale), ('surplus placeholder', surplus)):
            for key in keys if args.list else keys[:5]:
                print(f'    {label}: {key}')
            if not args.list and len(keys) > 5:
                print(f'    … {len(keys) - 5} more {label} (use --list)')
        print()

sys.exit(1 if rejected else 0)
