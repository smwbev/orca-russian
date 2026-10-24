#!/usr/bin/env python3
"""Сверяет версию и счётчик строк во всех файлах пакета. Запускать ПЕРЕД тегом.

Запуск из корня репозитория: python3 tools/release-check.py

Дважды подряд (v5.1.27, v5.1.28) тег вставал на коммит, где docs/readme/README.ru.md
ещё показывал прошлую версию: заход правил английский README и забывал русский.
Двигать опубликованный тег нельзя, поэтому единственная защита — проверка до тега.

Сверяются только места, описывающие ТЕКУЩИЙ выпуск. Исторические упоминания
(«переведено начиная с версии пакета 5.1.7») и размер английского каталога
в шапке GLOSSARY — не расхождения.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (файл, regex с группой 1 = значение, что это) — по одному на каждое релизное место.
VERSION_SITES = [
    (r'badge/(?:version|версия)-(5\.1\.\d+)-', 'бейдж версии'),
    (r'(?:Package version|Версия пакета) (5\.1\.\d+)', 'alt бейджа'),
    (r'orca-russian\.git#v(5\.1\.\d+)', 'строка установки'),
    (r'Актуально на `v(5\.1\.\d+)`', 'шапка глоссария'),
    (r'лимитам движка\*\* на v(5\.1\.\d+)', 'запас по лимитам'),
]
# Тысячи — любые две цифры. Раньше здесь стояло `1[23]`, и с 14 000 строк (v5.1.147)
# ни один шаблон не срабатывал: проверка счётчиков молча пропускала всё девять
# выпусков подряд и печатала «согласовано». Ниже есть страховка от повторения.
COUNT_SITES = [
    (r'badge/(?:strings|строк)-(\d{2}[,\s%]?(?:20)?\d{3})-', 'бейдж строк'),
    # Русское числительное согласуется с числом («12 460 строк», «12 461 строка»),
    # поэтому окончания в шаблонах свободные — иначе проверка молча пропустит место.
    (r'alt="(\d{2}[,\s]\d{3}) (?:translated strings|переведённ\w+ строк\w*)"', 'alt бейджа'),
    (r'\n\s*(\d{2}[,\s]\d{3}) (?:strings —|строк\w* —)', 'подзаголовок'),
    (r'(?:translation catalog|каталог переводов), (\d{2}[,\s]\d{3})', 'дерево файлов'),
    # `переведен[оаы]`: счётчик, оканчивающийся на 1, требует согласования
    # («переведена 12 371 строка»), и жёсткое «переведено» молча теряло место.
    # «переведены 16 684 строки» тоже по-русски, и 24.10 так же выпало из счёта.
    (r'переведен[оаы] (\d{2}[,\s]\d{3}) строк', 'шапка глоссария'),
]
DOCS = ['README.md', 'docs/readme/README.ru.md', 'GLOSSARY.md']
# Число добавочных плюральных форм называют рядом со счётчиком строк.
EXTRA_SITES = [
    (r'and (\d+) extra plural forms', 'добавочные формы'),
    (r'и (\d+) добавочн\w+ форм\w* множественного числа', 'добавочные формы'),
]
# Каждое релизное место поимённо. Страховка ниже ловила только ноль найденных счётчиков,
# а место, которое одно перестало находиться, выпадало из счёта молча: 24.10 проверка
# прошла по 21 месту из 22 и напечатала «согласовано». Новая формулировка, которую шаблон
# не узнаёт, теперь ошибка, а не тишина.
REQUIRED = {
    'README.md': {('версия', 'бейдж версии'), ('версия', 'alt бейджа'), ('версия', 'строка установки'),
                  ('счётчик', 'бейдж строк'), ('счётчик', 'alt бейджа'), ('счётчик', 'подзаголовок'),
                  ('счётчик', 'дерево файлов'), ('формы', 'добавочные формы')},
    'docs/readme/README.ru.md': {('версия', 'бейдж версии'), ('версия', 'alt бейджа'),
                                 ('версия', 'строка установки'), ('счётчик', 'бейдж строк'),
                                 ('счётчик', 'alt бейджа'), ('счётчик', 'подзаголовок'),
                                 ('счётчик', 'дерево файлов'), ('формы', 'добавочные формы')},
    'GLOSSARY.md': {('версия', 'шапка глоссария'), ('версия', 'запас по лимитам'),
                    ('счётчик', 'шапка глоссария'), ('формы', 'добавочные формы')},
}
seen = set()


def flat(o, p=''):
    out = {}
    for k, v in o.items():
        path = f'{p}.{k}' if p else k
        out.update({path: v} if isinstance(v, str) else flat(v, path))
    return out


manifest = json.load(open(os.path.join(ROOT, 'orca-plugin.json'), encoding='utf-8'))
version = manifest['version']
catalog = flat(json.load(open(os.path.join(ROOT, 'locales/ru-RU.json'), encoding='utf-8')))
# Добавочные формы множественного числа — русские добавки без английской пары. В счётчик
# строк и в покрытие они не входят, иначе число «переведено» перестало бы сходиться с
# каталогом Orca. Определяются по одному пакету: `_few` и `_many` всегда, `_one` — когда в
# пакете нет `_other` с той же базой (в каталоге Orca `_one` без `_other` не бывает;
# tools/build.py сверяет это правило с каталогом и останавливается, если оно нарушено).
extra_forms = [k for k in catalog if re.search(r'_(few|many)$', k)
               or (k.endswith('_one') and k[:-4] + '_other' not in catalog)]
lines = len(catalog) - len(extra_forms)
print(f'манифест: v{version}, каталог: {lines} строк (+{len(extra_forms)} добавочных форм)')

# Счётчик пишут тремя способами: 12,452 (англ.), 12 452 и 12%20452 (бейдж).
ok_counts = {f'{lines:,}', f'{lines // 1000} {lines % 1000:03d}', f'{lines // 1000}%20{lines % 1000:03d}'}


# В русском тексте разряды разделяет НЕразрывный пробел — типографски это верно,
# а `\s` в шаблонах его ловит, поэтому сверять надо по нормализованному виду.
def norm(s):
    return s.replace('\xa0', ' ').replace(' ', ' ')

errors, checked, counts_checked = [], 0, 0
for rel in DOCS:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding='utf-8').read()
    for pattern, what in VERSION_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            seen.add((rel, 'версия', what))
            if found != version:
                errors.append(f'{rel} ({what}): {found} вместо {version}')
    for pattern, what in COUNT_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            counts_checked += 1
            seen.add((rel, 'счётчик', what))
            if norm(found) not in ok_counts:
                errors.append(f'{rel} ({what}): {found} вместо {lines}')

extra_checked = 0
for rel in DOCS:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    text = open(path, encoding='utf-8').read()
    for pattern, what in EXTRA_SITES:
        for found in set(re.findall(pattern, text)):
            checked += 1
            extra_checked += 1
            seen.add((rel, 'формы', what))
            if int(found) != len(extra_forms):
                errors.append(f'{rel} ({what}): {found} вместо {len(extra_forms)}')
if extra_forms and not extra_checked:
    errors.append('в пакете есть добавочные формы, но документация их число не называет')

# Английский остаток: заголовок раздела обязан равняться сумме своих пунктов и совпадать
# в обоих README. До v5.1.157 заголовок считали от main (365), а пункты объясняли только
# остаток релиза (316) — число в заголовке не сходилось с собственной разбивкой.
REMAINDER = {
    'README.md': (r'([\d,]+) keys of the Orca v[\d.]+ catalog stay in English',
                  r'\n- \*\*([\d,]+) (?:strings?|keys?)\*\*', 'The list shrinks'),
    'docs/readme/README.ru.md': (r'(\d[\d\s\xa0]*) ключ\w* каталога Orca v[\d.]+ оста\w+ английск',
                                 r'\n- \*\*(\d[\d\s\xa0]*) (?:строк\w*|ключ\w*)\*\*', 'Список сокращается'),
}
headlines = {}
for rel, (head_re, item_re, stop) in REMAINDER.items():
    text = open(os.path.join(ROOT, rel), encoding='utf-8').read()
    m = re.search(head_re, text)
    if not m or stop not in text[m.end():]:
        errors.append(f'{rel}: не найден раздел английского остатка — шаблон REMAINDER устарел')
        continue
    checked += 1
    head = int(re.sub(r'\D', '', m.group(1)))
    body = text[m.end():text.index(stop, m.end())]
    total = sum(int(re.sub(r'\D', '', v)) for v in re.findall(item_re, body))
    headlines[rel] = head
    if total != head:
        errors.append(f'{rel}: в заголовке остатка {head}, а пункты в сумме дают {total}')
if len(set(headlines.values())) > 1:
    errors.append(f'заголовок остатка расходится между README: {headlines}')

# Ноль найденных счётчиков — это сломанные шаблоны, а не чистый выпуск.
if not counts_checked:
    errors.append('ни один счётчик строк не найден — шаблоны COUNT_SITES устарели')
for rel, sites in REQUIRED.items():
    for kind, what in sorted(sites - {(k, w) for r, k, w in seen if r == rel}):
        errors.append(f'{rel}: не найдено место «{what}» ({kind}) — формулировку правили, '
                      f'шаблон её не узнаёт')

for e in sorted(set(errors)):
    print('  ✗', e)
if errors:
    print(f'\n❌ {len(set(errors))} расхождений в {checked} местах — тег не ставить')
    sys.exit(1)
print(f'\n✅ версия и счётчики согласованы, проверено мест: {checked}')
