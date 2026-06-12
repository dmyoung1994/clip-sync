# 📋 clip-sync

A lightweight, cross-platform daemon that automatically syncs your clipboard across any machine on your local network using a central [Microbin](https://github.com/danielszabo99/microbin) instance.

## 🚀 One-Line Installation

### **macOS / Linux / WSL**
```bash
curl -sSL https://github.com/dmyoung1994/clip-sync/raw/master/install.sh | bash
```

### **Windows (PowerShell)**
```powershell
iwr -useb https://github.com/dmyoung1994/clip-sync/raw/master/install.ps1 | iex
```

---

## 🛠️ Manual Installation (Local Development)

If you are running this from your local cloned repository:

```bash
# Navigate to the folder
cd Documents/GitHub/clip-sync

# Install the package and its dependencies
pip install .
```

## ⚙️ Usage

After installation, start the sync daemon by pointing it to your Host's Microbin URL:

```bash
clip-sync --hub http://192.168.68.62:8081
```

### Options
| Flag | Description | Default |
| :--- | :--- | :--- |
| `--hub` | **(Required)** The URL of your Microbin hub | N/A |
| `--interval` | How often to check for changes (in seconds) | `1.0` |

## 🏗️ Requirements

- **Central Hub:** A running [Microbin](https://github.com/danielszabo99/microbin) instance on a static IP on your network.
- **Python:** 3.8 or higher.
- **Dependencies:** `pyperclip`, `requests`.

## 🛡️ Security Note
This tool operates on your local network. Ensure your Microbin instance is only accessible to trusted devices on your private network.
