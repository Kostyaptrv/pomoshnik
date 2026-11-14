"""Скрипт для диагностики автообновления."""

import sys
import json
import urllib.request
import io

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_github_release():
    """Проверяет, создан ли релиз на GitHub."""
    
    print("=" * 70)
    print("🔍 ДИАГНОСТИКА АВТООБНОВЛЕНИЯ")
    print("=" * 70)
    
    # Конфигурация
    GITHUB_REPO = "Kostyaptrv/pomoshnik"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    CURRENT_VERSION = "1.0"
    
    print(f"\n📌 Текущая версия: {CURRENT_VERSION}")
    print(f"📌 Репозиторий: {GITHUB_REPO}")
    print(f"📌 URL API: {GITHUB_API_URL}")
    print()
    
    # Проверка 1: Доступность GitHub
    print("✓ Проверка 1: Подключение к GitHub...")
    try:
        req = urllib.request.Request(
            "https://api.github.com/rate_limit",
            headers={"User-Agent": "diagnostic-script"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            print(f"  ✅ GitHub API доступен")
            print(f"  📊 Лимит запросов: {data['resources']['core']['remaining']}/{data['resources']['core']['limit']}")
    except Exception as e:
        print(f"  ❌ Ошибка подключения к GitHub: {e}")
        print(f"  💡 Проверьте подключение к интернету")
        return False
    
    # Проверка 2: Доступность репозитория
    print(f"\n✓ Проверка 2: Репозиторий {GITHUB_REPO}...")
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{GITHUB_REPO}",
            headers={"User-Agent": "diagnostic-script"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            repo_data = json.loads(response.read().decode("utf-8"))
            print(f"  ✅ Репозиторий найден")
            print(f"  📝 Название: {repo_data.get('name')}")
            print(f"  📝 Описание: {repo_data.get('description')}")
            print(f"  📝 Звёзд: {repo_data.get('stargazers_count', 0)}")
    except urllib.error.HTTPError as e:
        print(f"  ❌ Репозиторий не найден (HTTP {e.code})")
        print(f"  💡 Создайте репозиторий: https://github.com/new")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False
    
    # Проверка 3: Релиз v1.0
    print(f"\n✓ Проверка 3: Релиз v1.0...")
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "diagnostic-script"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            release_data = json.loads(response.read().decode("utf-8"))
            
            tag = release_data.get("tag_name", "N/A")
            print(f"  ✅ Релиз найден!")
            print(f"  🏷️ Tag: {tag}")
            print(f"  📅 Опубликовано: {release_data.get('published_at', 'N/A')}")
            print(f"  📝 Описание: {release_data.get('body', 'N/A')[:100]}...")
            
            # Проверяем ассеты
            assets = release_data.get("assets", [])
            print(f"\n  📎 Ассеты ({len(assets)} файлов):")
            exe_found = False
            for asset in assets:
                name = asset.get("name", "")
                size = asset.get("size", 0)
                download_count = asset.get("download_count", 0)
                size_mb = size / (1024 * 1024)
                
                print(f"    - {name}")
                print(f"      Размер: {size_mb:.1f} MB")
                print(f"      Скачиваний: {download_count}")
                
                if name.endswith(".exe") and "Помощник" in name:
                    exe_found = True
                    print(f"      ✅ Найден установщик!")
            
            if not exe_found:
                print(f"\n  ⚠️  WARNING: .exe файл не найден в релизе!")
                print(f"  💡 Прикрепите installer/Помощник_установщик_1.0.exe к релизу")
            
            # Проверка версии
            latest_version = tag.lstrip("v")
            if latest_version == CURRENT_VERSION:
                print(f"\n  ✅ Версии совпадают: {CURRENT_VERSION}")
                print(f"  💡 Автообновление НЕ предложит установку (это правильно)")
            else:
                print(f"\n  🔄 Версии разные: текущая {CURRENT_VERSION}, последняя {latest_version}")
                if compare_versions(latest_version, CURRENT_VERSION) > 0:
                    print(f"  💡 Доступно обновление!")
                else:
                    print(f"  💡 У вас более новая версия")
            
            return True
            
    except urllib.error.HTTPError as e:
        print(f"  ❌ Релиз не найден (HTTP {e.code})")
        if e.code == 404:
            print(f"\n  🔴 ПРОБЛЕМА НАЙДЕНА!")
            print(f"  💡 Релиз v1.0 не создан на GitHub")
            print(f"  📋 Создайте релиз:")
            print(f"     1. Откройте: https://github.com/Kostyaptrv/pomoshnik/releases/new")
            print(f"     2. Tag: v1.0")
            print(f"     3. Title: Версия 1.0")
            print(f"     4. Прикрепите installer/Помощник_установщик_1.0.exe")
            print(f"     5. Нажмите Publish release")
        return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False
    
    return True

def compare_versions(v1: str, v2: str) -> int:
    """Сравнивает две версии. Возвращает 1 если v1 > v2, -1 если v1 < v2, 0 если равны."""
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]
    
    while len(parts1) < len(parts2):
        parts1.append(0)
    while len(parts2) < len(parts1):
        parts2.append(0)
    
    for p1, p2 in zip(parts1, parts2):
        if p1 > p2:
            return 1
        if p1 < p2:
            return -1
    
    return 0

if __name__ == "__main__":
    print()
    success = check_github_release()
    print()
    print("=" * 70)
    if success:
        print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА УСПЕШНО")
        print("💡 Если релиз создан, но автообновление не работает:")
        print("   1. Проверь логи приложения: data/logs/app_YYYYMMDD.log")
        print("   2. Запусти приложение с флагом -v для verbose логов")
        print("   3. Убедись, что GITHUB_REPO в utils/updater.py = Kostyaptrv/pomoshnik")
    else:
        print("❌ ПРОБЛЕМА НАЙДЕНА! Следуй рекомендациям выше.")
    print("=" * 70)
    print()
