"""Скрипт проверки состояния словарей."""
import json
import sys
import os

print("=" * 60)
print("Проверка состояния проекта")
print("=" * 60)

# Проверка словаря рифм
print("\nСловарь рифм:")
try:
    with open('data/rhymes_dict.json', 'r', encoding='utf-8') as f:
        rhymes = json.loads(f.read())
    print(f"  OK Слов: {len(rhymes)}")
    print(f"  Примеры: {list(rhymes.keys())[:5]}")
except Exception as e:
    print(f"  ERROR: {e}")

# Проверка библиотеки фраз
print("\nБиблиотека фраз:")
try:
    sys.path.insert(0, '.')
    from engine.phrases import PHRASES
    print(f"  OK Категорий: {len(PHRASES)}")
    for cat, phrases in PHRASES.items():
        print(f"     - {cat}: {len(phrases)} фраз")
except Exception as e:
    print(f"  ERROR: {e}")

# Проверка данных
print("\nФайлы данных:")
data_dir = 'data'
if os.path.exists(data_dir):
    for file in os.listdir(data_dir):
        if file.endswith('.json'):
            path = os.path.join(data_dir, file)
            size = os.path.getsize(path)
            print(f"  - {file}: {size} bytes")

print("\n" + "=" * 60)
print("OK Проверка завершена!")
print("=" * 60)
