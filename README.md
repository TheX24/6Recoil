> [!IMPORTANT]
>
> ## I haven't been playing the game much lately, so I probably won't be updating the program very often, if at all.
> 

<div align="center">
  <img src="/6Recoilbanner.png?raw=true" alt="6Recoil Banner" />
  <img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg"/>
</div>

## Features
- 🎮 **Easy Controls**
  - Start/Stop button for quick activation
  - Caps Lock toggle functionality
  - Always-on-top window option
  - Automatic chat message shortcuts (F1-F5)
  - Random operator selection

- ⚙️ **Customization**
  - Adjustable vertical and horizontal recoil control
  - Customizable RPM settings per weapon
  - Toggle options for:
    - Secondary weapon auto-disable
    - Caps Lock chat writing
    - Window always-on-top

- 💬 **Chat Integration**
  - Quick chat messages (F1-F5):
    - "good luck have fun"
    - "good game well played"
    - "nice try"
    - "nice shot"
    - "good job"
  - Customizable chat messages

## Installation
1. Download the latest release from the releases page
2. Extract the files to your preferred location
3. Run `6Recoil v1.4.exe`

## Setup Guide
1. Launch the program
2. Enter the shooting range
3. Select an operator
4. Enable custom speed settings
5. Configure the weapon's RPM
6. Fine-tune recoil values:
   - Vertical: Increase if recoil is present
   - Horizontal: Positive values move right, negative values move left
7. Configure weapon presets:
   - Navigate to the `_internal` folder
   - Open `speed_options_new.txt`
   - Clear existing content
   - Add weapons using format: `{name} = {vertical}, {horizontal}, {rpm}`
   - Save the file

## Usage
1. Launch 6Recoil
2. Click the Start button
3. Select your current weapon (auto-applies settings)
4. Toggle Caps Lock to activate
5. ADS and shoot

## Building from Source
### Prerequisites
- Python 3.x
- Required dependencies (see requirements.txt)

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
   pyinstaller --name "6Recoil" --windowed --icon=icon.ico --add-data "attack_operators.txt;." --add-data "defense_operators.txt;." --add-data "speed_options_new.txt;." --add-data "icon.ico;." --add-data "config.ini;." 6Recoil_v1.4.pyw
   ```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Disclaimer
This software is for educational purposes only. Use at your own risk and ensure compliance with the terms of service of the games you play.
