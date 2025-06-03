# MetaFetch

A beautiful, fast, and comprehensive system information tool inspired by neofetch, written in Python with enhanced cross-platform support and advanced system monitoring capabilities.

```bash
                   -`                    john@desktop
                  .o+`                   -------------
                 `ooo/                   OS: Ubuntu 22.04.3 LTS
                `+oooo:                  Kernel: 5.15.0-84-generic
               `+oooooo:                 Architecture: x86_64
               -+oooooo+:                Uptime: 2d 14h 32m
             `/:-:++oooo+:               Packages: 2847 (apt), 23 (pip), 45 (npm)
            `/++++/+++++++:              Shell: bash 5.1.16
           `/++++++++++++++:             Desktop: GNOME
          `/+++ooooooooo+/`              Window Manager: Mutter
         ./ooosssso++osssssso+`          Terminal: gnome-terminal
        .oossssso-````/ossssss+`         CPU: Intel i7-9700K (8C/16T)
       -osssssso.      :ssssssso.        GPU: NVIDIA GeForce RTX 3070
      :osssssss/        osssso+++.       Memory: 8.2GB / 32.0GB (26%)
     /ossssssss/        +ssssooo/-       Swap: 2.1GB / 8.0GB (26%)
   `/ossssso+/:-        -:/+osssso+-     Disk: 245.8GB / 931.5GB (26%)
  `+sso+:-`                 `.-/+oso:    Network: eth0 (192.168.1.100)
 `++:.                           `-/+/   Resolution: 2560x1440
 .`                                 `/   Battery: 85% (Charging)
                                        Temperature: 45.2°C
                                        Load Avg: 0.85, 1.23, 1.45
                                        Processes: 342
                                        Users: john (tty1), admin (pts/0)
                                        Public IP: 203.0.113.45
                                        Timezone: America/New_York
                                        Python: Python 3.10.12
                                        Session: X11 | Wayland
```

---

## 🌟 Features

### Core Functionality
- **🌍 Cross-Platform Support**: Works seamlessly on Linux, macOS, and Windows
- **📊 Comprehensive System Info**: 25+ system metrics including hardware, software, and network information
- **🎨 Beautiful ASCII Art**: Platform-specific ASCII logos with colorful ANSI output
- **⚡ Fast Performance**: Optimized information gathering with timeout protection
- **🔧 Multiple Display Modes**: Full display with ASCII art or compact categorized view

### Advanced System Detection
- **📦 Package Manager Detection**: Supports 12+ package managers:
  - System: `apt`, `dnf/yum`, `pacman`, `portage`, `xbps`, `apk`
  - Cross-platform: `brew`, `pip`, `conda`, `npm`, `gem`, `cargo`
- **🖥️ Desktop Environment Detection**: Auto-detects DE (GNOME, KDE, XFCE, MATE, etc.) and standalone WMs
- **🌐 Network Information**: Active interfaces, local IPs, and public IP detection
- **🔋 Hardware Monitoring**: Real-time battery, temperature, memory, disk, and swap usage
- **👥 Multi-user Support**: Shows all logged-in users and their terminals
- **📺 Display Information**: Screen resolution and session type detection

### Technical Features
- **🛡️ Robust Error Handling**: Graceful degradation when information isn't available
- **⏱️ Timeout Protection**: Prevents hanging on slow system commands
- **🔄 Fallback Methods**: Multiple detection methods for maximum compatibility
- **📱 Responsive Design**: Adapts output formatting based on available information

---

## 🚀 Installation

### Prerequisites
Ensure you have Python 3.6 or higher installed:
```bash
python --version
# or
python3 --version
```

### Install from Source
1. **Clone the repository:**
```bash
git clone https://github.com/volksgeistt/metafetch.git
cd metafetch
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
# or for system-wide installation
pip3 install -r requirements.txt
```

3. **Make it executable (Linux/macOS):**
```bash
chmod +x metafetch.py
```

### System-wide Installation (Optional)
**Linux/macOS:**
```bash
# Method 1: Create symbolic link
sudo ln -s $(pwd)/metafetch.py /usr/local/bin/metafetch

# Method 2: Add to PATH
echo 'export PATH="$PATH:'$(pwd)'"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
```cmd
# Add the directory to your PATH environment variable
# or create a batch file in a directory that's already in PATH
```

---

## 📖 Usage

### Basic Usage
```bash
# Run with Python
python metafetch.py
python3 metafetch.py

# If installed globally
metafetch
```

### Command Line Options
```bash
metafetch [OPTIONS]

Options:
  -c, --compact     Display compact categorized output without ASCII art
  -h, --help        Show help message and usage information
  --version         Show version information
```

### Usage Examples

**Full system information with ASCII art (default):**
```bash
metafetch
```

**Compact categorized display:**
```bash
metafetch -c
```
```
john@desktop
============

System:
  OS: Ubuntu 22.04.3 LTS
  Kernel: 5.15.0-84-generic
  Architecture: x86_64
  Uptime: 2d 14h 32m

Software:
  Packages: 2847 (apt), 23 (pip), 45 (npm)
  Shell: bash 5.1.16
  Desktop: GNOME
  Terminal: gnome-terminal

Hardware:
  CPU: Intel i7-9700K (8C/16T)
  GPU: NVIDIA GeForce RTX 3070
  Memory: 8.2GB / 32.0GB (26%)
  Disk: 245.8GB / 931.5GB (26%)

Network:
  Local IP: eth0 (192.168.1.100)
  Public IP: 203.0.113.45
  Resolution: 2560x1440

Status:
  Battery: 85% (Charging)
  Temperature: 45.2°C
  Load Avg: 0.85, 1.23, 1.45
  Processes: 342
```

---

## 🎨 Customization

MetaFetch is highly customizable and extensible:

### Color Customization
Modify the `colors` dictionary in the `metafetch` class:
```python
self.colors = {
    'red': '\033[91m',
    'green': '\033[92m',
    # Add your custom colors
}
```

### ASCII Art Customization
Edit the `get_ascii_art()` method to add custom ASCII art or modify existing ones.

### Information Fields
- **Add new fields**: Create new `get_*()` methods and add them to `gather_info()`
- **Remove fields**: Comment out unwanted information in the display methods
- **Modify display**: Customize the `display()` or `display_compact()` methods

### Example Customization
```python
# Add custom information
def get_favorite_editor(self):
    return os.environ.get('EDITOR', 'Unknown')

# Add to info_functions in gather_info()
'editor': self.get_favorite_editor,
```

---

## 🔧 Compatibility

### Operating Systems
| OS | Support | Versions | Features |
|---|---|---|---|
| **Linux** | ✅ Full | All major distributions | Complete feature set |
| **macOS** | ✅ Full | macOS 10.12+ (Sierra and later) | Complete feature set |
| **Windows** | ✅ Full | Windows 10/11 | Complete feature set |

### Package Managers
#### System Package Managers
- **Linux**: `apt` (Debian/Ubuntu), `dnf`/`yum` (RHEL/Fedora), `pacman` (Arch), `portage` (Gentoo), `xbps` (Void), `apk` (Alpine)
- **macOS**: `brew` (Homebrew)

#### Language Package Managers
- **Python**: `pip`, `conda`
- **JavaScript**: `npm`
- **Ruby**: `gem`
- **Rust**: `cargo`

### Desktop Environments & Window Managers
#### Desktop Environments
- GNOME, KDE Plasma, XFCE, MATE, Cinnamon, LXQt, LXDE, Budgie, Pantheon

#### Window Managers
- **Tiling**: i3, bspwm, awesome, dwm, sway, Hyprland
- **Stacking**: openbox, fluxbox, JWM, IceWM

---

## 🛠️ Technical Details

### Dependencies
- **psutil**: System and process utilities
- **Built-in modules**: os, platform, subprocess, socket, getpass, time, sys, datetime, re, urllib

### Performance
- **Startup time**: < 1 second on modern systems
- **Memory usage**: ~10-20MB during execution
- **CPU usage**: Minimal, with 3-second timeout protection

### Security Considerations
- Commands executed with timeout protection
- No user input processing (command injection safe)
- External network requests limited to IP detection services
- File system access uses proper exception handling

---

## 🤝 Contributing

We welcome contributions! Here are some ways you can help:

1. **Report bugs** by opening an issue
2. **Suggest features** or improvements
3. **Submit pull requests** with bug fixes or new features
4. **Improve documentation** or add examples
5. **Test on different platforms** and report compatibility issues

### Development Setup
```bash
git clone https://github.com/volksgeistt/metafetch.git
cd metafetch
pip install -r requirements.txt
python metafetch.py  # Test your changes
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by [neofetch](https://github.com/dylanaraps/neofetch) and [screenfetch](https://github.com/KittyKatt/screenFetch)
- Thanks to all contributors who help improve MetaFetch
- Special thanks to the Python community for excellent libraries like `psutil`

---

## 📊 Comparison with Similar Tools

| Feature | MetaFetch | neofetch | screenfetch | fastfetch |
|---|---|---|---|---|
| Language | Python | Bash | Bash | C |
| Cross-platform | ✅ | ✅ | ❌ | ✅ |
| Package Detection | 12+ managers | 50+ managers | Limited | Many |
| Performance | Fast | Medium | Slow | Very Fast |
| Customization | High | Very High | Medium | Medium |
| Dependencies | psutil only | Many | Many | Minimal |
| Compact Mode | ✅ | ❌ | ❌ | ✅ |

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/volksgeistt">Ujjawal Singh</a></sub>
  <br>
  <sub>If you find MetaFetch useful, please consider giving it a ⭐!</sub>
</div>
