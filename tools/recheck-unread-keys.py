#!/usr/bin/env python3
"""Пересверяет tools/unread-catalog-keys.json с исходниками релиза Orca и main.

Запуск из корня репозитория, на каждом новом стабильном релизе Orca (без этого build.py
остановится):

    python3 tools/recheck-unread-keys.py                       # последний релиз и upstream/main
    python3 tools/recheck-unread-keys.py --release v1.4.243
    python3 tools/recheck-unread-keys.py --add orphans.txt     # дописать новых сирот

Нужна локальная копия stablyai/orca с тегами (`--orca`, по умолчанию ~/Developer/orca);
скрипт только читает её через `git archive`. Ключ уходит из списка, если он сам или его
база без суффикса множественного числа встречается строковым литералом в .ts/.tsx релиза
или main, а также если его нет ни в одном из двух en.json. `--add` принимает вывод
`config/scripts/verify-localization-orphans.mjs` из stablyai/orca#22056 (первая строка —
сводка) и дописывает только тех сирот, которых не читает и релиз.
"""
import argparse, datetime, io, json, os, re, subprocess, sys, tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, 'tools', 'unread-catalog-keys.json')
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
LITERAL = re.compile(r"""['"`]([A-Za-z][A-Za-z0-9._-]{6,})['"`]""")
PLURAL = re.compile(r'_(zero|one|two|few|many|other)$')
# Ключи, которые обязаны встретиться в любой живой сборке: дважды самодельный сбор литералов
# молча отдавал пустой список, и всё выглядело «нечитаемым».
PROBES = ('auto.components.settings.AppearancePane', 'sessionSearch.panel', 'auto.components.skills')

parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
parser.add_argument('--orca', default=os.path.expanduser('~/Developer/orca'), help='копия stablyai/orca с тегами')
parser.add_argument('--release', help='тег релиза (по умолчанию последний стабильный)')
parser.add_argument('--main', default='upstream/main', help='ref живого main (у форка origin/main отстаёт)')
parser.add_argument('--add', help='вывод verify-localization-orphans.mjs: сироты main для дописывания')
args = parser.parse_args()


def git(*a, binary=False):
    r = subprocess.run(['git', '-C', args.orca, *a], capture_output=True, text=not binary)
    if r.returncode != 0:
        sys.exit(f'✗ git {" ".join(a[:2])}: {(r.stderr if not binary else r.stderr.decode()).strip()}')
    return r.stdout


def flat(o, p=''):
    out = {}
    for k, v in o.items():
        path = f'{p}.{k}' if p else k
        out.update(flat(v, path) if isinstance(v, dict) else {path: v})
    return out


def literals(ref):
    archive = tarfile.open(fileobj=io.BytesIO(git('archive', ref, 'src', 'mobile', binary=True)))
    found, files = set(), 0
    for member in archive:
        name = member.name
        if not member.isfile() or '/locales/' in name or not name.endswith(('.ts', '.tsx')):
            continue
        files += 1
        found.update(LITERAL.findall(archive.extractfile(member).read().decode('utf-8', 'replace')))
    missing = [p for p in PROBES if not any(p in s for s in found)]
    if files < 10000 or len(found) < 30000 or missing:
        sys.exit(f'✗ {ref}: {files} файлов, {len(found)} литералов, нет контрольных {missing} — сбор неполный')
    print(f'  {ref}: {files} файлов, {len(found)} литералов')
    return found


release = args.release or subprocess.run(
    ['gh', 'release', 'view', '--repo', 'stablyai/orca', '--json', 'tagName', '--jq', '.tagName'],
    capture_output=True, text=True).stdout.strip()
if not release:
    sys.exit('✗ последний релиз не определился (gh недоступен?) — укажи --release')
main_sha = git('rev-parse', '--short=11', args.main).strip()
catalogs = [flat(json.loads(git('show', f'{ref}:{EN_PATH}'))) for ref in (release, main_sha)]
read = literals(release) | literals(main_sha)


def is_read(k):
    return k in read or PLURAL.sub('', k) in read


doc = json.load(open(LIST, encoding='utf-8'))
before = doc['keys']
revived = sorted(k for k in before if is_read(k))
gone = sorted(k for k in before if not is_read(k) and not any(k in c for c in catalogs))
keys = set(before) - set(revived) - set(gone)
added = []
if args.add:
    orphans = [l.strip() for l in open(args.add, encoding='utf-8').read().splitlines()[1:] if l.strip()]
    added = sorted(k for k in orphans if k not in keys and not is_read(k) and any(k in c for c in catalogs))
    keys |= set(added)

doc['keys'] = sorted(keys)
doc['checked'].update(release=release, main=main_sha, date=datetime.date.today().isoformat())
open(LIST, 'w', encoding='utf-8').write(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
print(f'\n✅ {os.path.relpath(LIST, ROOT)}: {len(before)} → {len(keys)} ключей, сверено с {release} и main {main_sha}')
for label, items in (('снова читается — уйдёт обратно в пакет', revived),
                     ('исчез из обоих каталогов', gone), ('дописан', added)):
    if items:
        print(f'  {label}: {len(items)}')
        for k in items[:10]:
            print(f'    {k}')
        if len(items) > 10:
            print(f'    … ещё {len(items) - 10}')
