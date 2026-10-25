#!/usr/bin/env python3
"""Собирает locales/ru-RU.json из блоков перевода и валидирует по правилам Orca.

Запуск из корня репозитория:

    python3 tools/build.py

Нужны python3 и авторизованный `gh`: правило защиты и каталог берутся из последнего
стабильного релиза stablyai/orca. Рабочий каталог с блоками перевода — `.i18n-work/`
(в git не входит); другой путь задаётся переменной ORCA_RU_WORK. Без блоков сборка
просто перепроверяет уже собранный каталог и записывает его без изменений.
"""
import json, re, glob, sys, os, subprocess, base64

# Флагов у сборки нет, а любой запуск перезаписывает каталог: `--help` молча собирал
# пакет (22.10 так прошла незапланированная сборка). Справка — этот докстринг, прочие
# аргументы — ошибка до первого обращения к сети.
if sys.argv[1:] in (['-h'], ['--help']):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    sys.exit(f'✗ build.py запускается без аргументов, получено: {" ".join(sys.argv[1:])} (справка: --help)')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.environ.get('ORCA_RU_WORK') or os.path.join(ROOT, '.i18n-work')
TARGET = os.path.join(ROOT, 'locales', 'ru-RU.json')
REPO = 'stablyai/orca'
EN_PATH = 'src/renderer/src/i18n/locales/en.json'
PROT = 'auto.components.settings.'
DANGEROUS = {'__proto__', 'prototype', 'constructor'}
RAW = ['-H', 'Accept: application/vnd.github.raw+json']

# Правило защиты берём из ПОСЛЕДНЕГО СТАБИЛЬНОГО РЕЛИЗА Orca, а не из main.
# Урок v5.1.4: allow-list из PR #12455 уже был в main, но ещё не в релизе, и пакет
# с 34 разрешёнными ключами отклонялся целиком у всех, кто на v1.4.168 — русский
# язык просто переставал загружаться. Пакет обязан работать на том, что установлено.
CHROME = set()
_stable = subprocess.run(['gh', 'release', 'view', '--repo', REPO, '--json', 'tagName', '--jq', '.tagName'],
                         capture_output=True, text=True).stdout.strip()
if _stable:
    _r = subprocess.run(['gh', 'api',
        f'repos/{REPO}/contents/src/shared/plugins/plugin-translatable-chrome.ts?ref={_stable}',
        '--jq', '.content'], capture_output=True, text=True)
    if _r.returncode == 0 and _r.stdout.strip():
        src = base64.b64decode(_r.stdout).decode('utf-8')
        CHROME = set(re.findall(r"'(auto\.components\.settings\.[^']+)'", src))
# Компоненты, защищённые целиком, без исключений (с stablyai/orca#33069: карточка одобрения в
# нативном чате, бейдж «Official», баннер подсказки типа файла). Их список лежит в самом модуле
# движка, а не в plugin-translatable-chrome.ts; в релизах до v1.4.240 его нет. Модуль переехал
# в artifacts/ — ищем по обоим путям.
COMPONENTS = []
if _stable:
    for _path in ('src/shared/plugins/artifacts/plugin-language-pack-artifact.ts',
                  'src/shared/plugins/plugin-language-pack-artifact.ts'):
        _r = subprocess.run(['gh', 'api', *RAW, f'repos/{REPO}/contents/{_path}?ref={_stable}'],
                            capture_output=True, text=True)
        if _r.returncode == 0 and _r.stdout.strip():
            _m = re.search(r'PROTECTED_TRANSLATION_COMPONENTS\s*=\s*\[(.*?)\]', _r.stdout, re.S)
            COMPONENTS = re.findall(r"'([^']+)'", _m.group(1)) if _m else []
            break
    print(f'  правило защиты: релиз {_stable}, разрешённых исключений {len(CHROME)}, '
          f'защищённых компонентов {len(COMPONENTS)}')

def protected(path):
    if any(path == c or path.startswith(c + '.') for c in COMPONENTS):
        return True
    if not path.startswith(PROT):
        return False
    if path in CHROME:
        return False
    return path[len(PROT):].lower().startswith('plugin')

def fetch_catalog(ref):
    # Сырой media type, а не `.content`: для файла крупнее 1 МиБ contents API отдаёт
    # пустой `.content` без ошибки. Каталог релиза v1.4.223 весит 984 904 Б.
    rc = subprocess.run(['gh', 'api', *RAW, f'repos/{REPO}/contents/{EN_PATH}?ref={ref}'],
                        capture_output=True, text=True)
    return json.loads(rc.stdout) if rc.returncode == 0 and rc.stdout.strip() else {}

# Каталог main: рабочий снимок, если он есть, иначе свежий с GitHub.
_en_snapshot = os.path.join(SCRATCH, 'en.json')
if os.path.exists(_en_snapshot):
    en = json.load(open(_en_snapshot, encoding='utf-8'))
else:
    en = fetch_catalog('main')
    if not en:
        sys.exit('✗ каталог main не загрузился (gh недоступен или ответ пуст) — сборка остановлена')

# Каталог релиза — второй источник истины. Пакет ставится людям, у которых
# установлен релиз, а не main: ключ, уже удалённый из main, но живой в релизе,
# всё ещё нужен им переведённым. Обратное тоже верно — ключ из main готовим
# заранее. Поэтому валидным считаем ключ, присутствующий хотя бы в одном из двух.
en_release = fetch_catalog(_stable) if _stable else {}

# Без каталога релиза сборка сочтёт ключи, живые только в релизе, удалёнными:
# выбросит их из пакета и посоветует убрать из блоков. Лучше не собрать ничего.
if not en_release:
    sys.exit('✗ каталог релиза не загрузился (gh недоступен или ответ пуст) — сборка остановлена')

def get(d, path):
    cur = d
    for p in path.split('.'):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur if isinstance(cur, str) else None

def placeholders(s):
    return sorted(re.findall(r'\{\{[^}]*\}\}', s))

# Русскому нужны формы, которых в английском каталоге нет. i18next ищет их для любого
# вызова с параметром `count`: к ключу, который назвал компонент, приписывается суффикс
# формы, и только потом берётся сам ключ. Отсюда два вида добавочных форм:
#   - `_few` и `_many` у семейства, где в каталоге Orca есть `<база>_one` и `<база>_other`;
#   - `_one`, `_few` и `_many` у строки, которую Orca зовёт со счётчиком, но хранит одним
#     текстом (`fileOther`, `connectedHostCount_other`, `transcriptsSkipped`). Сам ключ
#     остаётся запасным вариантом для дробей.
# Сегодня движок выбирает только между `_one` и остальным: пакет регистрируется под
# синтетическим кодом `plugin<hex>` (stablyai/orca#12106). Формы `_few`/`_many` заложены
# заранее и заработают в день, когда смержат stablyai/orca#12505. Поэтому строка, которая
# достаётся «остальным» числам, по-прежнему обязана читаться при любом числе
# («сохранено веток: 5»).
PLURAL_EXTRA = re.compile(r'_(one|few|many)$')

def plural_family(k):
    m = PLURAL_EXTRA.search(k)
    return k[:m.start()] if m else None

def plural_sources(k):
    """Английские образцы для добавочной формы; пусто, если ключ обычный или опоры нет."""
    base = plural_family(k)
    if base is None or get(en, k) is not None or get(en_release, k) is not None:
        return []
    return [s for cat in (en, en_release) for name in (base + '_other', base + '_one', base)
            if (s := get(cat, name)) is not None]

def plural_companions(k):
    """Ключи, без которых добавочная форма повисает: семейство либо сама строка."""
    base = plural_family(k)
    if get(en, base + '_other') is not None or get(en_release, base + '_other') is not None:
        return [base + '_one', base + '_other']
    return [base]

# --- база: уже собранный каталог, чтобы блоки в рабочем каталоге не были единственным источником ---
flat = {}
dupes = []
if os.path.exists(TARGET):
    def flatten(o, p=''):
        for k, v in o.items():
            path = f'{p}.{k}' if p else k
            if isinstance(v, str):
                flat[path] = v
            else:
                flatten(v, path)
    flatten(json.load(open(TARGET, encoding='utf-8')))
    print(f'  база {os.path.basename(TARGET)}: {len(flat)} строк')
# блок всегда сильнее базы: правка в блоке должна переписывать уже собранный каталог.
# конфликтом считается только расхождение между двумя блоками.
from_block = {}
for f in sorted(glob.glob(os.path.join(SCRATCH, 'wave*-ru-part*.json'))):
    part = json.load(open(f, encoding='utf-8'))
    for k, v in part.items():
        if k in from_block and from_block[k] != v:
            dupes.append(k)
        from_block[k] = v
        flat[k] = v
    print(f'  + {os.path.basename(f)}: {len(part)} строк')

errors, warnings = [], []
for k in dupes:
    errors.append(f'ключ {k} задан в двух блоках по-разному')

# --- сверка с английским каталогом ---
# Ключ, исчезнувший из каталога Orca, — не ошибка: апстрим переименовал или удалил
# строку. Такие записи молча выпадают из пакета, но ошибкой считаются, если пришли
# из блока перевода (значит, блок пора править), а не из уже собранного каталога.
# Добавочная форма уходит вместе со своей опорой.
retired = [k for k in flat
           if get(en, k) is None and get(en_release, k) is None and not plural_sources(k)]
for k in retired:
    if k in from_block:
        errors.append(f'ключа {k} нет в en.json — убрать из блока перевода')
    else:
        warnings.append(f'{k}: исчез из каталога Orca, выброшен из пакета')
    del flat[k]

# Защищённый ключ в базе — след прошлой сборки, сделанной по правилам ещё не
# вышедшего релиза. Выбрасываем молча-с-предупреждением: пакет должен грузиться
# на том, что установлено. Приход такого ключа из блока — ошибка автора.
for k in [k for k in flat if protected(k)]:
    if k not in from_block:
        warnings.append(f'{k}: защищён в релизе {_stable or "?"}, выброшен из пакета')
        del flat[k]

extra_forms = []
for k, v in flat.items():
    extra = plural_sources(k)
    if extra:
        extra_forms.append(k)
        # Без опоры в пакете при сегодняшнем резолвере число, для которого формы нет,
        # осталось бы английским.
        for companion in plural_companions(k):
            if companion not in flat:
                errors.append(f'{k}: в пакете нет {companion} — форма без своей опоры')
    src = get(en, k) or get(en_release, k) or (extra[0] if extra else None)
    if src is None:
        errors.append(f'ключа {k} нет ни в main, ни в релизе')
        continue
    # Появление плейсхолдера, которого нет в оригинале, — ошибка: подставлять нечего.
    # Пропуск английского суффикса множественного числа ({{value1}} = "s") — норма для русского.
    # Сверяем с обеими версиями строки: main и релиз расходятся неделями, и перевод,
    # верный для установленной у людей сборки, не должен падать из-за того, что main
    # уже переписал текст. Пример: 92924a14e3 — в v1.4.184 «Review inactive workspaces
    # ({{value0}})», в main «Clean up workspaces» без плейсхолдера.
    variants = extra or [s for s in (get(en, k), get(en_release, k)) if s is not None]
    known = {p for s in variants for p in placeholders(s)}
    # Формы семейства обслуживает один вызов с `count`: `_one` вправе взять его из `_other`,
    # даже когда английская единица обходится без числа («Reopen terminal»).
    if not extra and (base := plural_family(k)) and any(
            '{{count}}' in (get(cat, base + '_other') or '') for cat in (en, en_release)):
        known.add('{{count}}')
    extra_ph = [p for p in placeholders(v) if p not in known]
    dropped = [p for p in placeholders(src) if p not in placeholders(v)]
    if extra_ph:
        errors.append(f'в {k} появился плейсхолдер, которого нет в оригинале: {extra_ph}')
    if dropped:
        warnings.append(f'{k}: опущен {dropped} — убедиться, что это английский суффикс, а не данные')
    if len(v) > 8192:
        errors.append(f'{k} длиннее 8192 символов')
    if protected(k):
        errors.append(f'{k} — защищённый ключ, пакет будет отклонён целиком')
    if src != v and not re.search(r'[а-яА-ЯёЁ]', v) and re.search(r'[a-zA-Z]{4}', v):
        warnings.append(f'{k} без кириллицы: {v!r}')
    if 'ё' not in v and re.search(r'(все|ещ)е\b', v.lower()):
        warnings.append(f'{k}: возможно пропущена «ё» — {v!r}')

# release-check.py считает добавочные формы без каталога Orca, по одному пакету: `_few` и
# `_many` всегда, `_one` — когда в пакете нет `_other` с той же базой. Расхождение значит,
# что в каталоге Orca появился ключ, ломающий это правило, и счётчики в документации врут.
_by_shape = {k for k in flat if re.search(r'_(few|many)$', k)
             or (k.endswith('_one') and k[:-4] + '_other' not in flat)}
if _by_shape != set(extra_forms):
    odd = sorted(_by_shape ^ set(extra_forms))
    errors.append(f'добавочные формы посчитаны двумя способами по-разному: {odd[:5]}')

# --- разворачиваем в дерево ---
tree = {}
for k, v in sorted(flat.items()):
    parts = k.split('.')
    cur = tree
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
        if not isinstance(cur, dict):
            errors.append(f'конфликт структуры на {k}')
            break
    else:
        cur[parts[-1]] = v

# --- лимиты движка ---
nodes = [0]
maxdepth = [0]
def walk(o, path='', depth=0):
    maxdepth[0] = max(maxdepth[0], depth)
    for k, v in o.items():
        nodes[0] += 1
        if not k or len(k) > 128 or k in DANGEROUS or '.' in k or any(ord(c) <= 31 for c in k):
            errors.append(f'небезопасный ключ {k}')
        if isinstance(v, dict):
            walk(v, f'{path}.{k}', depth + 1)
walk(tree)

raw = json.dumps(tree, ensure_ascii=False, indent=2) + '\n'
size = len(raw.encode('utf-8'))
if nodes[0] > 20000: errors.append(f'узлов {nodes[0]} > 20000')
if maxdepth[0] > 16: errors.append(f'глубина {maxdepth[0]} > 16')
if size > 5 * 1024 * 1024: errors.append('файл больше 5 МБ')

print()
for w in warnings[:15]: print('  ⚠', w)
if len(warnings) > 15: print(f'  ⚠ … ещё {len(warnings)-15}')
for e in errors: print('  ✗', e)

if errors:
    print(f'\n❌ {len(errors)} ошибок — файл не записан')
    sys.exit(1)

open(TARGET, 'w', encoding='utf-8').write(raw)
print(f'\n✅ записан {TARGET}')
# «Строк» — переводы строк каталога Orca. Добавочные формы считаются отдельно:
# английских пар у них нет, и в покрытие они не входят.
print(f'   строк: {len(flat) - len(extra_forms)} (+{len(extra_forms)} добавочных форм), '
      f'узлов: {nodes[0]}/20000, глубина: {maxdepth[0]}/16, размер: {size} Б/5 МБ')
