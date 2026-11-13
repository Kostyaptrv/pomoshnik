with open('ui/pages/editor_page.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[476:500], start=476):
        print(f"{i}: {repr(line)}")
