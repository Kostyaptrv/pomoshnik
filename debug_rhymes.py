import sys
import os

sys.path.insert(0, r"C:\Users\kot35\IdeaProjects\pomoshnik")

from engine.rhymes import _data_path

path = _data_path('rhymes_dict.json')
print(f"Path: {path}")
print(f"Exists: {os.path.exists(path)}")

if os.path.exists(path):
    import json
    with open(path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        print(f"Words: {len(data)}")
else:
    # Try to find where rhymes_dict.json actually is
    src = r"C:\Users\kot35\IdeaProjects\pomoshnik\data\rhymes_dict.json"
    print(f"Source exists: {os.path.exists(src)}")
    
    # Check if we're running from frozen
    print(f"Frozen: {getattr(sys, 'frozen', False)}")
    if getattr(sys, 'frozen', False):
        print(f"Exe dir: {os.path.dirname(sys.executable)}")
