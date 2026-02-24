# 6Recoil

> [!CAUTION]
> With Y11, the script may be detected. Use at your own risk.

<div align="center">
  <img src="/6Recoilbanner.png?raw=true" alt="6Recoil Banner" />
  <img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="AGPL-3.0 License"/>
</div>

## Features

- 🎮 **Dual Weapon Control**
  - Separate recoil profiles for primary and secondary weapons
  - Independent Start/Stop toggle for each weapon slot
  - Quick switch between weapons using `1`/`2` keys
  - If a weapon slot has no auto weapon, switching to it turns off CapsLock instead of applying recoil
  - Both slots can be active simultaneously for full independent control

- 🎯 **Precision Controls**
  - CapsLock-based activation (toggle on = recoil active)
  - Chat Detection (CD): automatically disables recoil on `T`/`Y` and re-enables on `Enter`/`Esc`
  - Always-on-top window option
  - Random operator selection (attacker/defender)
  - Sub-pixel remainder accumulation for smooth fractional movement

- 🛡️ **Anti-Detection**
  - Gaussian-distributed recoil variation — matches natural human jitter distribution
  - Per-shot timing jitter (+-5% of RPM interval) — avoids fixed-interval detection
  - Random start delay (10-60ms) before recoil kicks in — simulates human reaction time

- ⚙️ **Advanced Customization**
  - Adjustable vertical and horizontal recoil per weapon slot
  - Configurable RPM per weapon slot
  - Preset system via `.txt` files for quick weapon switching
  - Custom speed override mode with live entry fields
  - Configurable variation range

- 💬 **Chat Macros (RF)**
  - Send preset messages with F1-F5:
    - F1: `glhf` (customizable)
    - F2: `ggwp` (customizable)
    - F3: `nt` (customizable)
    - F4: `nice` (customizable)
    - F5: `good job` (customizable)
  - All messages editable in the Config window

## Installation

1. Download the latest release from the [releases page](https://github.com/TheX24/6Recoil/releases)
2. Extract the files to your preferred location
3. Run `6Recoil v1.5.exe`

## Setup Guide

### Weapon Presets

1. Navigate to the `_internal` folder
2. Open `speed_main_options.txt` (primary) and `speed_secondary_options.txt` (secondary)
3. Add weapons using the format:
   ```
   WEAPON_NAME = vertical, horizontal, rpm
   ```
   Example:
   ```
   416-C_CARBINE = 7, 0, 800
   F2 = 9, 0, 980
   BEARING_9 = 3, 0, 1100
   ```
4. Save both files — presets appear in the dropdowns on next launch

### Calibrating Recoil

1. Launch the program and enter the in-game shooting range
2. Toggle the **Primary** or **Secondary** Start button for the slot you want to calibrate
3. Enable **CapsLock** to activate recoil control
4. ADS and fire at a wall:
   - Crosshair drifts **up** -> increase Vertical Speed
   - Crosshair drifts **down** -> decrease Vertical Speed
   - Crosshair drifts **right** -> use a negative Horizontal Speed value
   - Crosshair drifts **left** -> use a positive Horizontal Speed value
5. Enable **Variation** with a range of 0.5-1.5 for natural-looking movement
6. Save calibrated values to your preset files

### Config Window

Open via the **Config** button:

| Option | Description |
|--------|-------------|
| Always on Top | Keeps the window above the game |
| Enable CD | Chat Detection - auto CapsLock management |
| Enable RF | Enables F1-F5 chat macros |
| Enable Variation | Enables Gaussian recoil variation |
| Variation Range | Spread of variation (higher = more random) |
| Dark Mode | Toggles dark/light theme |
| Keypress Duration | RF macro keypress hold duration |
| Interval Between Keypresses | RF macro delay between keys |

## Usage

| Action | How |
|--------|-----|
| Activate recoil | Enable CapsLock |
| Deactivate recoil | Disable CapsLock |
| Toggle primary recoil | Click **Primary Start** |
| Toggle secondary recoil | Click **Secondary Start** |
| Switch to primary in-game | Press `1` |
| Switch to secondary in-game | Press `2` |
| Open chat (auto disables recoil) | `T` or `Y` (CD must be enabled) |
| Close chat (auto re-enables recoil) | `Enter` or `Esc` (CD must be enabled) |
| Send chat macro | `F1`-`F5` (RF must be enabled) |

> **Note:** Pressing `2` while Secondary is not toggled on turns CapsLock off automatically (no recoil for that slot). Same for `1` with Primary off. Switching back to an active slot restores CapsLock.

## Building from Source

### Prerequisites

- Python 3.x
- Dependencies listed in `requirements.txt`

### Build Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/TheX24/6Recoil.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build using PyInstaller:
   ```bash
   pyinstaller --name "6Recoil" --windowed --icon=icon.ico --add-data "attack_operators.txt;." --add-data "defense_operators.txt;." --add-data "speed_main_options.txt;." --add-data "speed_secondary_options.txt;." --add-data "icon.ico;." --add-data "config.ini;." 6Recoil_v1.5_fixed.pyw
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk and ensure compliance with the terms of service of the games you play.
