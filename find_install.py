import os
import winreg

# Check uninstall registry for Pomoshnik
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    for i in range(100):
        try:
            subkey = winreg.OpenKey(key, winreg.EnumKey(key, i))
            try:
                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                if "Pomoshnik" in display_name or "pomoshnik" in display_name.lower():
                    print(f"Found: {display_name}")
                    print(f"Location: {install_location}")
            except:
                pass
            winreg.CloseKey(subkey)
        except:
            break
    winreg.CloseKey(key)
except Exception as e:
    print(f"Registry error: {e}")

# Check Program Files (x86)
pf = r"C:\Program Files (x86)"
if os.path.exists(pf):
    print(f"\nContents of {pf}:")
    for item in os.listdir(pf):
        if "pom" in item.lower() or "пом" in item.lower():
            print(f"  {item}")
            full = os.path.join(pf, item)
            if os.path.isdir(full):
                data = os.path.join(full, "data")
                if os.path.exists(data):
                    print(f"    data files: {os.listdir(data)}")
