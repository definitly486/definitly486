# Скрипт проходит по указанной папке, находит все .pkg файлы, определяет имя пакета и его версию,
# нормализует версии, выбирает для каждого пакета последнюю (максимальную) версию и выводит список
# последних версий. В конце также выводятся найденные дубликаты (пакеты с несколькими версиями).

import os
from collections import defaultdict
from packaging import version

# Укажите путь к папке с пакетами
folder_path = "/ntfs-2TB/All15"

# Получаем все .pkg файлы в папке
files = [f for f in os.listdir(folder_path) if f.endswith(".pkg")]

# Функция для выделения имени пакета и версии
def split_name_version(pkg):
    name_ver = pkg[:-4]  # убираем .pkg
    parts = name_ver.rsplit('-', 1)  # разделяем по последнему дефису
    if len(parts) == 2:
        return parts[0], parts[1]
    return name_ver, "0"

# Функция нормализации версии
def normalize_version(ver):
    ver = ver.replace('_', '.').replace(',', '.')
    ver = ''.join(c if c.isdigit() or c == '.' else '' for c in ver)
    ver = ver.rstrip('.')
    if not ver:
        ver = "0"
    return ver

# Словарь: пакет -> список версий
all_versions = defaultdict(list)
for f in files:
    name, ver = split_name_version(f)
    all_versions[name].append(ver)

# Выбираем последние версии каждого пакета
latest_packages = {}
for name, vers in all_versions.items():
    latest = max(vers, key=lambda x: version.parse(normalize_version(x)))
    latest_packages[name] = latest

# Формируем итоговый список
result = [f"{name}-{ver}.pkg" for name, ver in latest_packages.items()]

# ---- вывод сначала последних версий ----
print("\nПоследние версии пакетов:")
for r in sorted(result):
    print(r)

# ---- вывод дубликатов в самом конце ----
print("\nНайдены дубликаты пакетов:")
found_duplicates = False
for name, vers in all_versions.items():
    if len(vers) > 1:
        found_duplicates = True
        sorted_vers = sorted(vers, key=lambda x: version.parse(normalize_version(x)))
        print(f"{name}: {', '.join(sorted_vers)}")

if not found_duplicates:
    print("Дубликатов не найдено.")
