import os

def fix_encoding(filename):
    if not os.path.exists(filename):
        print(f"Skipping {filename} (not found)")
        return

    content = None
    # Try reading with different encodings
    for enc in ['utf-8', 'utf-16', 'utf-16-le', 'cp1252', 'latin-1']:
        try:
            with open(filename, 'r', encoding=enc) as f:
                content = f.read()
            print(f"Read {filename} successfully with {enc}")
            break
        except Exception:
            continue
    
    if content is None:
        print(f"Failed to read {filename}")
        return

    # Write back as utf-8
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved {filename} as UTF-8")
    except Exception as e:
        print(f"Failed to write {filename}: {e}")

if __name__ == "__main__":
    fix_encoding('.env')
    fix_encoding('.env.local')
