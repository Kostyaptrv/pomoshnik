import sys
print(sys.executable)
print(sys.version)
try:
    import PyQt6
    print("PyQt6 found:", PyQt6.__file__)
except ImportError:
    print("PyQt6 NOT found")
