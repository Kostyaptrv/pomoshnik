"""Модуль автообновления через GitHub Releases."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Tuple

# Текущая версия приложения
APP_VERSION = "1.0"
APP_NAME = "Помощник для написания песен"

# URL GitHub репозитория (замени на свой!)
GITHUB_REPO = "Kostyaptrv/pomoshnik"  # owner/repo
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_current_version() -> str:
    """Возвращает текущую версию приложения."""
    return APP_VERSION


def check_for_updates(timeout: int = 10) -> Optional[dict]:
    """
    Проверяет наличие обновлений на GitHub.
    
    Returns:
        Словарь с информацией об обновлении или None:
        {
            "version": "1.1",
            "download_url": "...",
            "changelog": "...",
            "published_at": "2025-01-01T00:00:00Z"
        }
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"{APP_NAME}-Updater/{APP_VERSION}"
            }
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            
            # Проверяем, есть ли новая версия
            latest_version = data.get("tag_name", APP_VERSION).lstrip("v")
            
            if _compare_versions(latest_version, APP_VERSION) > 0:
                # Находим исполняемый файл в релизах
                asset = None
                for a in data.get("assets", []):
                    if "Помощник" in a.get("name", "") and a.get("name", "").endswith(".exe"):
                        asset = a
                        break
                
                if asset:
                    return {
                        "version": latest_version,
                        "download_url": asset["browser_download_url"],
                        "asset_name": asset["name"],
                        "changelog": data.get("body", "Исправления и улучшения"),
                        "published_at": data.get("published_at", ""),
                        "size": asset.get("size", 0),
                    }
            
            return None
            
    except urllib.error.URLError as e:
        print(f"[Updater] Network error: {e}")
        return None
    except json.JSONDecodeError:
        print("[Updater] Invalid JSON response")
        return None
    except Exception as e:
        print(f"[Updater] Unexpected error: {e}")
        return None


def _compare_versions(v1: str, v2: str) -> int:
    """
    Сравнивает две версии.
    
    Returns:
        1 если v1 > v2
        -1 если v1 < v2
        0 если равны
    """
    parts1 = [int(x) for x in v1.split(".")]
    parts2 = [int(x) for x in v2.split(".")]
    
    # Дополняем нулями
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


def download_update(download_url: str, progress_callback=None) -> Optional[str]:
    """
    Скачивает обновление.
    
    Args:
        download_url: URL для скачивания
        progress_callback: Функция вызываемая при прогрессе (current, total)
    
    Returns:
        Путь к скачанному файлу или None
    """
    try:
        temp_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            "update_download.exe"
        )
        
        # Создаём директорию если нет
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        def _progress(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                current = block_num * block_size
                progress_callback(current, total_size)
        
        urllib.request.urlretrieve(download_url, temp_path, _progress)
        return temp_path
        
    except Exception as e:
        print(f"[Updater] Download error: {e}")
        return None


def cleanup_update():
    """Удаляет скачанный файл обновления."""
    temp_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "update_download.exe"
    )
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except:
            pass


def format_size(size_bytes: int) -> str:
    """Форматирует размер вhuman-readable формат."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_date(date_str: str) -> str:
    """Форматирует дату публикации."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str
