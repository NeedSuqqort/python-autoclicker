# Python Auto Clicker

A desktop autoclicker with a graphical interface, configurable hotkeys, and a macro recorder for mouse and keyboard actions. **_UI update is in progress, Sorry!_**


## Requirements

- Python 3
- `customtkinter`
- `pynput`

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

or

```bash
uv add -r requirements.txt
```

## Run

From the project directory, start the application with:

```bash
python app.py
```

## Features

- Set the delay and mouse button for repeated clicks.
- Start or stop clicking with the button or toggle hotkey.
- Record, play, and delete mouse and keyboard macros.
- Configure hotkeys in the **Settings** tab.
- Save settings and macros in the `saves` directory.

Default hotkeys:

| Action | Key |
| --- | --- |
| Toggle autoclicker | `S` |
| Start macro recording | `F9` |
| Stop and save recording | `F10` |
| Play macro | `F11` |
| Delete macro | `F12` |
