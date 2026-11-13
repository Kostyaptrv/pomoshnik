"""Управление историей версий песен."""
import json
import os
from datetime import datetime
from typing import Optional, List


STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "versions")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _get_version_file(song_id: str) -> str:
    """Возвращает путь к файлу истории версий песни.
    
    Args:
        song_id: ID песни.
        
    Returns:
        Путь к JSON файлу с версией.
    """
    return os.path.join(STORAGE_DIR, f"{song_id}_versions.json")


def load_versions(song_id: str) -> List[dict]:
    """Загружает историю версий песни.
    
    Args:
        song_id: ID песни.
        
    Returns:
        Список версий (словарей с timestamp, version, snapshot).
    """
    version_file = _get_version_file(song_id)
    if not os.path.exists(version_file):
        return []
    
    with open(version_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_version(song_id: str, song_data: dict, comment: str = "") -> dict:
    """Сохраняет новую версию песни.
    
    Args:
        song_id: ID песни.
        song_data: Полные данные песни.
        comment: Комментарий к версии (необязательно).
        
    Returns:
        Словарь с информацией о сохранённой версии.
    """
    versions = load_versions(song_id)
    
    version_number = len(versions) + 1
    now = datetime.now().isoformat()
    
    version = {
        "version": version_number,
        "timestamp": now,
        "comment": comment,
        "stats": song_data.get("stats", {}),
        "sections_count": len(song_data.get("sections", {})),
        "filled_sections": sum(1 for s in song_data.get("sections", {}).values() if s.get("text", "").strip()),
        "total_lines": song_data.get("stats", {}).get("total_lines", 0),
    }
    
    versions.append(version)
    
    # Сохраняем метаданные версии
    with open(_get_version_file(song_id), "w", encoding="utf-8") as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)
    
    # Сохраняем полный снэпшот версии
    save_version_snapshot(song_id, version_number, song_data)
    
    # Авто-очистка старых версий
    cleanup_old_versions(song_id, keep_last=10)
    
    return version


def load_version_snapshot(song_id: str, version_number: int) -> Optional[dict]:
    """Загружает снэпшот конкретной версии.
    
    Args:
        song_id: ID песни.
        version_number: Номер версии.
        
    Returns:
        Словарь с данными песни или None.
    """
    snapshot_file = os.path.join(STORAGE_DIR, f"{song_id}_v{version_number}.json")
    if not os.path.exists(snapshot_file):
        return None
    
    with open(snapshot_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_version_snapshot(song_id: str, version_number: int, song_data: dict) -> bool:
    """Сохраняет полный снэпшот версии.
    
    Args:
        song_id: ID песни.
        version_number: Номер версии.
        song_data: Полные данные песни.
        
    Returns:
        True если сохранение успешно.
    """
    snapshot_file = os.path.join(STORAGE_DIR, f"{song_id}_v{version_number}.json")
    
    # Убираем некоторые поля для чистоты
    snapshot = {
        "version": version_number,
        "timestamp": song_data.get("updated_at", datetime.now().isoformat()),
        "title": song_data.get("title"),
        "style_id": song_data.get("style_id"),
        "sections": song_data.get("sections", {}),
        "stats": song_data.get("stats", {}),
    }
    
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    return True


def restore_version(song_id: str, version_number: int) -> Optional[dict]:
    """Восстанавливает песню из конкретной версии.
    
    Args:
        song_id: ID песни.
        version_number: Номер версии для восстановления.
        
    Returns:
        Словарь с данными песни или None.
    """
    snapshot = load_version_snapshot(song_id, version_number)
    if not snapshot:
        return None
    
    # Загружаем текущую песню
    from engine import editor
    song = editor.load_song(song_id)
    if not song:
        return None
    
    # Обновляем секции из снэпшота
    song["sections"] = snapshot.get("sections", {})
    song["stats"] = snapshot.get("stats", {})
    
    # Сохраняем обновлённую песню
    editor.save_song(song)
    
    return song


def get_version_summary(song_id: str) -> List[dict]:
    """Получает сводку по всем версиям песни.
    
    Args:
        song_id: ID песни.
        
    Returns:
        Список словарей с краткой информацией о версиях.
    """
    versions = load_versions(song_id)
    summary = []
    
    for v in versions:
        ts = v.get("timestamp", "")
        date_str = ts[:10] if ts else "N/A"
        time_str = ts[11:19] if len(ts) > 19 else "N/A"
        
        progress = 0
        if v.get("sections_count", 0) > 0:
            progress = v.get("filled_sections", 0) / v["sections_count"] * 100
        
        summary.append({
            "version": v["version"],
            "date": date_str,
            "time": time_str,
            "comment": v.get("comment", ""),
            "sections": f"{v.get('filled_sections', 0)}/{v.get('sections_count', 0)}",
            "lines": v.get("total_lines", 0),
            "progress": round(progress, 0),
        })
    
    return summary


def cleanup_old_versions(song_id: str, keep_last: int = 10) -> int:
    """Удаляет старые версии, оставляя только последние keep_last.
    
    Args:
        song_id: ID песни.
        keep_last: Сколько последних версий оставить.
        
    Returns:
        Количество удалённых версий.
    """
    versions = load_versions(song_id)
    
    if len(versions) <= keep_last:
        return 0
    
    # Версии, которые нужно удалить
    versions_to_delete = versions[:-keep_last]
    removed_count = 0
    
    for v in versions_to_delete:
        version_num = v.get("version")
        if version_num:
            snapshot_file = os.path.join(STORAGE_DIR, f"{song_id}_v{version_num}.json")
            if os.path.exists(snapshot_file):
                os.remove(snapshot_file)
                removed_count += 1
    
    # Обновляем метаданные — оставляем только последние keep_last версий
    versions[:] = versions[-keep_last:]
    
    # Перенумеруем версии
    for i, v in enumerate(versions, start=1):
        v["version"] = i
    
    # Сохраняем обновлённые метаданные
    with open(_get_version_file(song_id), "w", encoding="utf-8") as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)
    
    return removed_count
