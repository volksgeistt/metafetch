# MetaFetch
A beautiful, fast, and comprehensive system information tool inspired by neofetch, written in Python with enhanced cross-platform support.
```bash
-                                        john@desktop
                  .o+`                   -------------
                 `ooo/                   OS: Ubuntu 22.04.3 LTS
                `+oooo:                  Kernel: 5.15.0-84-generic
               `+oooooo:                 Uptime: 2d 14h 32m
               -+oooooo+:                Packages: 2847 (apt), 23 (pip)
             `/:-:++oooo+:               Shell: bash 5.1.16
            `/++++/+++++++:              Desktop: GNOME
           `/++++++++++++++:             Terminal: gnome-terminal
          `/+++ooooooooo+/`              CPU: Intel i7-9700K (8C)
         ./ooosssso++osssssso+`          GPU: NVIDIA GeForce RTX 3070
        .oossssso-````/ossssss+`         Memory: 8.2GB / 32.0GB (26%)
       -osssssso.      :ssssssso.        Disk: 245.8GB / 931.5GB (26%)
      :osssssss/        osssso+++.       Network: eth0 (192.168.1.100)
     /ossssssss/        +ssssooo/-       Resolution: 2560x1440
   `/ossssso+/:-        -:/+osssso+-
  `+sso+:-`                 `.-/+oso:     ███████████████████████████
 `++:.                           `-/+/    ███████████████████████████
 .`                                 `/
```
---
## 🌟 Features
- Cross-Platform Support: Works seamlessly on Linux, macOS, and Windows
- Comprehensive System Info: Display detailed information about your system
- Beautiful ASCII Art: Platform-specific ASCII logos with colorful output
- Multiple Display Modes: Full, minimal, and color palette display options
- Package Manager Detection: Supports multiple package managers (apt, dnf, pacman, brew, pip, npm, etc.)
- Desktop Environment Detection: Automatically detects DE and WM
- Network Interface Information: Shows active network interfaces
- Performance Monitoring: Real-time memory, disk, and swap usage
- Customizable Output: Easy to extend and modify
---
## 🚀 Installation
**Prerequisites**
- Make sure you have Python 3.6 or higher installed:
```bash
python --version
```
**Install from Source**
1. Clone the repository:
```bash
git clone https://github.com/volksgeistt/metafetch
cd metafetch
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Make it executable (Linux/macOS):
```bash
chmod +x metafetch.py
```
**System-wide Installation (Optional)**
Create a link to use `metafetch` from anywhere:
```bash
# Linux/macOS
sudo ln -s $(pwd)/metafetch.py /usr/local/bin/metafetch

# Or add to your PATH
export PATH="$PATH:$(pwd)"
```
---
## 📖 Usage
**Basic:**
```bash
python metafetch.py
# or if installed globally
metafetch
```
**Command Line Options:**
```bash
metafetch [OPTIONS]

Options:
  -m, --minimal     Display minimal system information
  -c, --colors      Show color palette demonstration
  --version         Show version information
  -h, --help        Show help message
```
---
## Examples
**Full system information (default):**
```bash
metafetch
```
**Minimal display:**
```
metafetch -m
```
**Color palette:**
```bash
metafetch -c
```
---
## 🎨 Customization
MetaFetch is highly customizable. You can modify:
- Colors: Edit the colors dictionary in the `metafetch` class
- ASCII Art: Modify the `get_ascii_art()` method
- Information Fields: Add or remove fields in the `collect_info()` method
- Display Format: Customize the `display()` method
---
## 🔧 Supported Systems
**Operating Systems**
- Linux: All major distributions (Ubuntu, Debian, Fedora, Arch, etc.)
- macOS: macOS 10.12+ (Sierra and later)
- Windows: Windows 10/11

**Package Managers**
- Linux: apt, dnf/yum, pacman, portage, xbps, apk
- macOS: brew
- Cross-platform: pip, conda, npm, gem, cargo

**Desktop Environments**
- GNOME, KDE Plasma, XFCE, MATE, Cinnamon
- Window Managers: i3, bspwm, awesome, dwm, openbox, fluxbox
---
<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/volksgeistt">Ujjawal Singh</a></sub>
</div>



