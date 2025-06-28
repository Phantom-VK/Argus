# Argus - Automated Productivity Tracker

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Release](https://img.shields.io/github/v/release/Phantom-VK/Argus?include_prereleases)
![Build](https://img.shields.io/github/workflow/status/Phantom-VK/Argus/Build)

Argus is a cross-platform desktop application that automatically tracks work activity through periodic screenshots and activity monitoring, helping users analyze their productivity patterns.

![Argus Screenshot](docs/screenshots/dashboard.png)  
*Main Application Window - [More Screenshots](#screenshots)*

## Features

- 🖥️ **Automatic Screenshot Capture**
  - Configurable time intervals (2-4 minutes)
  - Multi-monitor support
  - Smart activity detection

- ⏱️ **Accurate Time Tracking**
  - Real-time work hour calculation
  - Pause/resume functionality
  - Inactivity detection

- 🔐 **Secure Authentication**
  - Login/Registration system
  - API integration
  - User-specific data storage

- 📊 **Productivity Insights**
  - Screenshot timeline
  - Activity heatmaps (coming soon)
  - Weekly reports (coming soon)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Method 1: From Source
```bash
git clone https://github.com/Phantom-VK/Argus.git
cd Argus
pip install -r requirements.txt

# Run application
python src/argus/main.py
```

### Method 2: Download Executable
Download the latest release for your platform:

[![Windows](https://img.shields.io/badge/Download-Windows-blue?logo=windows)](https://github.com/Phantom-VK/Argus/releases)
[![macOS](https://img.shields.io/badge/Download-macOS-black?logo=apple)](https://github.com/Phantom-VK/Argus/releases)
[![Linux](https://img.shields.io/badge/Download-Linux-yellow?logo=linux)](https://github.com/Phantom-VK/Argus/releases)

## Usage

1. **Authenticate** with your credentials
2. **Start Tracking** when beginning work
3. **View Reports** in the dashboard (coming soon)
4. **Export Data** via the API integration

## Screenshots

| Login Window | Registration | Main Interface |
|--------------|-------------|----------------|
| ![Login](docs/screenshots/login.png) | ![Register](docs/screenshots/register.png) | ![Main](docs/screenshots/dashboard.png) |

## Technology Stack

- **Frontend**: 
  ![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.2-green)
- **Backend**: 
  ![Python](https://img.shields.io/badge/Python-3.13.3-blue)
- **Packaging**: 
  ![PyInstaller](https://img.shields.io/badge/PyInstaller-6.0.0-orange)
- **Dependencies**:
  ![MSS](https://img.shields.io/badge/MSS-10.0.0-yellow)
  ![Pynput](https://img.shields.io/badge/Pynput-1.8.1-lightgrey)

## Development

### Build Instructions
```bash
# Windows
scripts/build_win.bat

# macOS
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh

# Linux
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

### Project Structure
```
Argus/
├── src/              # Source code
│   ├── argus/        # Core application
├── scripts/          # Build scripts
├── docs/             # Documentation
└── requirements.txt  # Dependencies
```

## Contributing

Contributions are welcome! Please open an issue or submit a PR.

## License

MIT License - See [LICENSE](LICENSE) for details.

