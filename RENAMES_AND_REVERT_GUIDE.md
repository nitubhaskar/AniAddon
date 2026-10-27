# AniAddon Renames & Revert Guide

This document records all renames, identifier substitutions, file moves, and environment modifications made when transitioning the addon from **Otaku / Test** to **AniAddon**. If anything unexpected happens or if you want to restore previous states, follow the instructions in the [Revert Instructions](#revert-instructions) section below.

---

## 1. Quick Git Reference

| State | Git Branch / Commit | Addon ID | Addon Name |
| :--- | :--- | :--- | :--- |
| **Current (AniAddon)** | Branch `aniaddon` (commit `963b029`) | `plugin.video.aniaddon`, `context.aniaddon` | AniAddon |
| **Previous (Test)** | Commit `ecab49e` / branch `test-addon` | `plugin.video.test`, `context.test` | Test |
| **Original (Otaku)** | Branch `main` | `plugin.video.otaku`, `context.otaku` | Otaku |

---

## 2. Directory & File Renames

### 2.1 Addon Directories
| Old Path | New Path | Description |
| :--- | :--- | :--- |
| `plugin.video.test/` (or `plugin.video.otaku/`) | `plugin.video.aniaddon/` | Main video addon root directory |
| `context.test/` (or `context.otaku/`) | `context.aniaddon/` | Context menu addon root directory |

### 2.2 Python Modules & Scripts
| Old File Path | New File Path | Description |
| :--- | :--- | :--- |
| `.../resources/lib/OtakuBrowser.py` | `.../resources/lib/AniAddonBrowser.py` | Default metadata browser class |
| `.../resources/lib/indexers/otaku.py` | `.../resources/lib/indexers/aniaddon.py` | Primary anime list indexer |
| `.../resources/lib/indexers/otaku_next_up.py` | `.../resources/lib/indexers/aniaddon_next_up.py` | Next-up episodes indexer |

---

## 3. Code, Symbol, & Identifier Mappings

The table below details every string, setting, property, and class that was renamed:

| Category | Old Value (Test / Otaku) | New Value (AniAddon) | Affected Files / Usage |
| :--- | :--- | :--- | :--- |
| **Addon ID** | `plugin.video.test` / `plugin.video.otaku` | `plugin.video.aniaddon` | `addon.xml`, `control.py`, `default.py`, `Main.py` |
| **Context Addon ID** | `context.test` / `context.otaku` | `context.aniaddon` | `context.aniaddon/addon.xml`, `default.py` |
| **Addon Name** | `Test` / `Otaku` | `AniAddon` | `addon.xml` (name attribute), UI titles |
| **Plugin Route URL** | `plugin://plugin.video.test/` | `plugin://plugin.video.aniaddon/` | Routing calls, context menus, widget paths |
| **Context Route URL** | `plugin://context.test/` | `plugin://context.aniaddon/` | Context menu action links |
| **Window Property** | `Window().Property(test.*)` / `(otaku.*)` | `Window().Property(aniaddon.*)` | Skins XML (`anichart.xml`, `resolver.xml`, etc.) |
| **Window Logo Prop** | `aniaddon.logo` (was `otaku.logo`) | `aniaddon.logo` | `anichart.xml`, `anime_statistics.xml` |
| **Window Art Prop** | `test.art` / `otaku.art` | `aniaddon.art` | Skin dialogs, player window properties |
| **Constants** | `OTAKU_SYNC_COMPLETED` | `ANIADDON_SYNC_COMPLETED` | `control.py`, `database_sync.py` |
| **Browser Class** | `class OtakuBrowser` | `class AniAddonBrowser` | `AniAddonBrowser.py`, `Main.py` |
| **Indexer Class** | `class OtakuAPI` | `class AniAddonAPI` | `indexers/aniaddon.py`, `indexers/__init__.py` |
| **Settings Section** | `<section id="otaku">` | `<section id="aniaddon">` | `resources/settings.xml` |
| **Settings Category** | `<category id="otaku">` | `<category id="aniaddon">` | `resources/settings.xml` |
| **Settings Keys** | `context.test.<action>` | `context.aniaddon.<action>` | `resources/settings.xml`, `default.py` |
| **Settings Version** | `<setting id="otaku.version">` | `<setting id="aniaddon.version">` | `resources/settings.xml`, `service.py` |
| **Browser API Value** | `<setting id="browser.api">otaku</setting>` | `<setting id="browser.api">aniaddon</setting>` | `resources/settings.xml`, `Main.py` |
| **Debrid Agent** | `Agent: 'Otaku'` / `'Test'` | `Agent: 'AniAddon'` | `all_debrid.py`, `debrid_link.py`, `torbox.py` |
| **Strings PO ID 32000** | `msgstr "Otaku"` / `"Test"` | `msgstr "AniAddon"` | `resources/language/resource.language.en_gb/strings.po` |

---

## 4. Kodi System Symlinks & Userdata

### 4.1 Junction Links in Kodi Addons Directory (`%APPDATA%\Kodi\addons\`)
- **Old Symlinks**:
  - `C:\Users\Peace\AppData\Roaming\Kodi\addons\plugin.video.test`
  - `C:\Users\Peace\AppData\Roaming\Kodi\addons\context.test`
- **Current Symlinks (Active)**:
  - `C:\Users\Peace\AppData\Roaming\Kodi\addons\plugin.video.aniaddon` &rarr; `...\scratch\Otaku-Testing\plugin.video.aniaddon`
  - `C:\Users\Peace\AppData\Roaming\Kodi\addons\context.aniaddon` &rarr; `...\scratch\Otaku-Testing\context.aniaddon`

### 4.2 Userdata Directory (`%APPDATA%\Kodi\userdata\addon_data\`)
- **Old Directory**:
  - `C:\Users\Peace\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.test`
- **Current Directory (Active)**:
  - `C:\Users\Peace\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.aniaddon`
  - All cached databases (`cache.db`, `malSync.db`, `mappings.db`), calendars, and settings were copied over.
  - Setting keys in `settings.xml` inside `addon_data` were updated from `context.test.*` to `context.aniaddon.*` and `browser.api` to `aniaddon`.
  - The old `plugin.video.test` userdata folder was **preserved** as a backup.

---

## 5. Revert Instructions

If you ever wish to revert any or all changes, choose one of the options below:

### Option A: Revert Code to `Test` via Git (Undo only AniAddon rename)
Run in PowerShell:
```powershell
cd "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing"
git checkout test-addon
```
*Or revert the specific commit on the current branch:*
```powershell
cd "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing"
git revert 963b029 --no-edit
```

### Option B: Revert Kodi Junctions to `Test`
Run in PowerShell:
```powershell
# Remove AniAddon junctions
Remove-Item "$env:APPDATA\Kodi\addons\plugin.video.aniaddon"
Remove-Item "$env:APPDATA\Kodi\addons\context.aniaddon"

# Re-create Test junctions
New-Item -ItemType Junction -Path "$env:APPDATA\Kodi\addons\plugin.video.test" -Target "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing\plugin.video.test"
New-Item -ItemType Junction -Path "$env:APPDATA\Kodi\addons\context.test" -Target "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing\context.test"
```

### Option C: Revert Completely to Original `Otaku`
Run in PowerShell:
```powershell
# 1. Switch git branch back to main
cd "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing"
git checkout main

# 2. Re-create Kodi junctions for original Otaku
Remove-Item -ErrorAction SilentlyContinue "$env:APPDATA\Kodi\addons\plugin.video.aniaddon"
Remove-Item -ErrorAction SilentlyContinue "$env:APPDATA\Kodi\addons\context.aniaddon"
Remove-Item -ErrorAction SilentlyContinue "$env:APPDATA\Kodi\addons\plugin.video.test"
Remove-Item -ErrorAction SilentlyContinue "$env:APPDATA\Kodi\addons\context.test"

New-Item -ItemType Junction -Path "$env:APPDATA\Kodi\addons\plugin.video.otaku" -Target "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing\plugin.video.otaku"
New-Item -ItemType Junction -Path "$env:APPDATA\Kodi\addons\context.otaku" -Target "C:\Users\Peace\.gemini\antigravity\scratch\Otaku-Testing\context.otaku"
```
