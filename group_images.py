import os
import re
import shutil

IMAGES_DIR = 'static/images'

# Regex to match files ending with m/f before the extension
def get_base_name(filename):
    match = re.match(r'(.+?)([mf])\.(jpg|jpeg|png)$', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def group_images():
    for filename in os.listdir(IMAGES_DIR):
        if not os.path.isfile(os.path.join(IMAGES_DIR, filename)):
            continue
        base = get_base_name(filename)
        if base:
            folder = os.path.join(IMAGES_DIR, base)
            os.makedirs(folder, exist_ok=True)
            src = os.path.join(IMAGES_DIR, filename)
            dst = os.path.join(folder, filename)
            shutil.move(src, dst)
            print(f"Moved {filename} to {folder}/")

if __name__ == "__main__":
    group_images() 