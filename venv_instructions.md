# Python Virtual Environment Activation Guide

To activate a Python virtual environment (assuming it was created using `python3 -m venv myapp`), find the appropriate command for your operating system and shell below.

## Activation Commands

| Operating System | Shell | Command |
| :--- | :--- | :--- |
| **Windows** | Command Prompt (CMD) | `myapp\Scripts\activate.bat` |
| **Windows** | PowerShell | `.\myapp\Scripts\Activate.ps1` * |
| **macOS / Linux** | Bash / Zsh | `source myapp/bin/activate` |
| **macOS / Linux** | Fish | `source myapp/bin/activate.fish` |

> ***Note for Windows PowerShell:** If you receive a script execution error, you may need to update your execution policy. Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first, then try activating again.*

---

## Managing Dependencies (`requirements.txt`)

Once your virtual environment is active, it's best practice to keep track of the packages you install. This allows others (or you on a different machine) to easily recreate the exact same environment.

* **Create or Update:** To save a list of all currently installed packages and their exact versions into a text file, run:
  ```bash
  pip freeze > requirements.txt