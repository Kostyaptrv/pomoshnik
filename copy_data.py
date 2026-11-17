import os
import shutil

src = r"C:\Users\kot35\IdeaProjects\pomoshnik\data"
dst = r"C:\Program Files (x86)\Pomoshnik\data"

print(f"Source: {src}")
print(f"Dest: {dst}")
print(f"Source exists: {os.path.exists(src)}")

if os.path.exists(src):
    files = os.listdir(src)
    print(f"Files in source: {files}")
    
    # Create dest if not exists
    if not os.path.exists(dst):
        os.makedirs(dst)
        print(f"Created dest: {dst}")
    
    # Copy each json file
    for f in files:
        if f.endswith(".json"):
            src_file = os.path.join(src, f)
            dst_file = os.path.join(dst, f)
            shutil.copy2(src_file, dst_file)
            size = os.path.getsize(dst_file)
            print(f"Copied {f}: {size} bytes")
