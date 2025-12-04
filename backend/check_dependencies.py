import os
import sys
import importlib
import pkgutil

# Add the current directory to sys.path
sys.path.append(os.getcwd())

def check_imports(start_dir):
    print(f"Checking imports in {start_dir}...")
    error_count = 0
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(".py") and file != "check_dependencies.py" and file != "run.py":
                module_path = os.path.join(root, file)
                module_name = os.path.relpath(module_path, os.getcwd()).replace(os.sep, ".")[:-3]
                
                try:
                    importlib.import_module(module_name)
                    # print(f"✅ {module_name}")
                except ImportError as e:
                    print(f"❌ {module_name}: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"⚠️ {module_name} (Runtime Error): {e}")
                    # We ignore runtime errors for now as we just want to check dependencies
                    pass
    
    if error_count == 0:
        print("\n🎉 All modules imported successfully!")
    else:
        print(f"\nFound {error_count} import errors.")

if __name__ == "__main__":
    check_imports("app")
