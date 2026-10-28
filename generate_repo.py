import os
import shutil
import zipfile
import hashlib
import xml.etree.ElementTree as ET

repo_root = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.join(repo_root, "repository.aniaddon")
os.makedirs(repo_dir, exist_ok=True)

# 1. Create repository.aniaddon/addon.xml
addon_xml_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="repository.aniaddon" name="AniAddon Repository" version="1.0.0" provider-name="TeamAniAddon">
    <extension point="xbmc.addon.repository" name="AniAddon Repository">
        <dir>
            <info compressed="false">https://raw.githubusercontent.com/nitubhaskar/AniAddon/main/repo/addons.xml</info>
            <checksum>https://raw.githubusercontent.com/nitubhaskar/AniAddon/main/repo/addons.xml.md5</checksum>
            <datadir zip="true">https://raw.githubusercontent.com/nitubhaskar/AniAddon/main/repo/zips/</datadir>
        </dir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>AniAddon Repository</summary>
        <description>Repository for AniAddon anime streaming and context menu addons.</description>
        <platform>all</platform>
        <assets>
            <icon>icon.png</icon>
            <fanart>fanart.jpg</fanart>
        </assets>
    </extension>
</addon>
"""

with open(os.path.join(repo_dir, "addon.xml"), "w", encoding="utf-8") as f:
    f.write(addon_xml_content.strip())

# Copy artwork to repository.aniaddon
for art in ["icon.png", "fanart.jpg"]:
    src = os.path.join(repo_root, "plugin.video.aniaddon", art)
    dst = os.path.join(repo_dir, art)
    if os.path.exists(src):
        shutil.copy2(src, dst)

# 2. Package repository.aniaddon into repository.aniaddon-1.0.zip
dist_dir = os.path.join(repo_root, "dist")
os.makedirs(dist_dir, exist_ok=True)
repo_zip_path = os.path.join(dist_dir, "repository.aniaddon-1.0.zip")

with zipfile.ZipFile(repo_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, repo_root)
            zf.write(full, rel)

print(f"Created: {repo_zip_path} ({os.path.getsize(repo_zip_path)} bytes)")

# 3. Create repo/ directory for Kodi repository hosting
kodi_repo_dir = os.path.join(repo_root, "repo")
zips_dir = os.path.join(kodi_repo_dir, "zips")
os.makedirs(zips_dir, exist_ok=True)

# Also create subdirectories inside zips/ matching Kodi conventions
for addon_name in ["plugin.video.aniaddon", "context.aniaddon", "repository.aniaddon"]:
    addon_zip_dir = os.path.join(zips_dir, addon_name)
    os.makedirs(addon_zip_dir, exist_ok=True)

# Copy zips and artwork to zips/
shutil.copy2(repo_zip_path, os.path.join(zips_dir, "repository.aniaddon", "repository.aniaddon-1.0.0.zip"))
shutil.copy2(repo_zip_path, os.path.join(zips_dir, "repository.aniaddon", "repository.aniaddon-1.0.zip"))
shutil.copy2(os.path.join(dist_dir, "context.aniaddon.zip"), os.path.join(zips_dir, "context.aniaddon", "context.aniaddon-6.0.0.zip"))
shutil.copy2(os.path.join(dist_dir, "plugin.video.aniaddon.zip"), os.path.join(zips_dir, "plugin.video.aniaddon", "plugin.video.aniaddon-6.0.0.zip"))

# Copy icon and fanart to addon zip dirs
for name in ["plugin.video.aniaddon", "context.aniaddon", "repository.aniaddon"]:
    src_folder = os.path.join(repo_root, name)
    dst_folder = os.path.join(zips_dir, name)
    for art in ["icon.png", "fanart.jpg"]:
        art_src = os.path.join(src_folder, art)
        if os.path.exists(art_src):
            shutil.copy2(art_src, os.path.join(dst_folder, art))

# 4. Generate repo/addons.xml
addons_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
for name in ["repository.aniaddon", "context.aniaddon", "plugin.video.aniaddon"]:
    xml_path = os.path.join(repo_root, name, "addon.xml")
    if os.path.exists(xml_path):
        with open(xml_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("<?xml"):
                    continue
                addons_xml += line
addons_xml += "</addons>\n"

addons_xml_path = os.path.join(kodi_repo_dir, "addons.xml")
with open(addons_xml_path, "w", encoding="utf-8") as f:
    f.write(addons_xml)

# Generate MD5 checksum
md5_hash = hashlib.md5(addons_xml.encode("utf-8")).hexdigest()
with open(os.path.join(kodi_repo_dir, "addons.xml.md5"), "w", encoding="utf-8") as f:
    f.write(md5_hash)

print(f"Created: {addons_xml_path} and addons.xml.md5 ({md5_hash})")
print("Repository setup complete!")
