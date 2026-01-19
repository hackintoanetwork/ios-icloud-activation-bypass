# iOS iCloud Activation Bypass

A Python-based iCloud activation bypass tool for iOS 12.x devices using checkra1n jailbreak.

## Supported Devices & iOS Versions

- **Devices**: iPhone 5s, iPhone 6, iPhone 6 Plus, iPad Mini 2/3, iPad Air 1, iPod Touch 6 (A7 devices)
- **iOS**: 12.0 - 12.5.7

## Requirements

- macOS / Linux / Windows
- Python 3.8+
- checkra1n jailbroken device
- USB connection to device

## Installation
```bash
git clone https://github.com/hackintoanetwork/ios-icloud-activation-bypass.git
cd ios-icloud-activation-bypass
pip3 install -r requirements.txt
```

## Usage

### 1. Jailbreak your device with checkra1n

- Download checkra1n: https://checkra.in/
- checkm8 exploit technical details: https://habr.com/en/companies/dsec/articles/472762/

### 2. Run the bypass tool
```bash
python3 bypass.py
```

The tool will automatically:
1. Detect your iOS device via USB
2. Transfer the patched `mobileactivationd` to `/var/root/`
3. Execute bypass commands:
   - Remount filesystem as read-write
   - Unload original mobileactivationd
   - Replace with patched version
   - Run uicache
   - Reload mobileactivationd

### 3. Complete activation

After the script finishes, tap **"Connect to iTunes"** on your device.

## Additional Tools

### ios_ssh.py

Interactive SSH shell and file transfer utility.
```bash
# Interactive shell
python3 ios_ssh.py

# Transfer file to device
python3 ios_ssh.py -t  
```

#### File Transfer Examples
```bash
# Transfer mobileactivationd to /var/root/
python3 ios_ssh.py -t ./mobileactivationd /var/root/mobileactivationd

# Transfer a script to device
python3 ios_ssh.py -t ./my_script.sh /var/root/my_script.sh

# Transfer to /usr/bin/
python3 ios_ssh.py -t ./my_binary /usr/bin/my_binary
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `-t`, `--transfer` | Transfer file: requires two parameters (local path, remote path) |
| `-s`, `--shell` | Start interactive SSH shell (default if no arguments) |

## How It Works

The bypass works by replacing the `mobileactivationd` binary with a patched version where all `Unactivated` strings are changed to `Activated`. This tricks iOS into thinking the device is already activated.

**Note**: This is a tethered bypass. After reboot, you need to re-jailbreak and run the bypass again.

### SCP transfer fails

The device may not have sftp-server. The tool uses SCP protocol which should work on most jailbroken devices.
