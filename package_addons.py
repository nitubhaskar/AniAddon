import os
import zipfile

repo_root = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(repo_root, "dist")
os.makedirs(dist_dir, exist_ok=True)

def zip_addon(folder_name, zip_name):
    folder_path = os.path.join(repo_root, folder_name)
    zip_path = os.path.join(dist_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for file in files:
                if file.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_root)
                zf.write(full_path, rel_path)
    print(f"Packaged: {zip_path} ({os.path.getsize(zip_path)} bytes)")

if __name__ == "__main__":
    zip_addon("context.aniaddon", "context.aniaddon.zip")
    zip_addon("plugin.video.aniaddon", "plugin.video.aniaddon.zip")
    print("Done! Both zips are ready in the dist/ folder.")
