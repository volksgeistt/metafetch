import os
import platform
import subprocess
import socket
import psutil
import getpass
import time
import sys
from datetime import datetime, timedelta
import re
import urllib.request

class metafetch:
    def __init__(self):
        self.info = {}
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'gray': '\033[90m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def run_command(self, cmd, timeout=3):
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_os_info(self):
        try:
            system = platform.system()
            
            if system == "Linux":
                sources = ['/etc/os-release', '/etc/lsb-release', '/etc/redhat-release']
                for source in sources:
                    try:
                        with open(source, 'r') as f:
                            content = f.read()
                            if 'PRETTY_NAME=' in content:
                                for line in content.split('\n'):
                                    if line.startswith('PRETTY_NAME='):
                                        return line.split('=')[1].strip().strip('"')
                            elif source == '/etc/redhat-release':
                                return content.strip()
                    except:
                        continue
                        
                lsb = self.run_command(['lsb_release', '-d'])
                if lsb:
                    return lsb.split('\t')[1] if '\t' in lsb else lsb
                    
                return f"Linux {platform.release()}"
                
            elif system == "Darwin":
                version = self.run_command(['sw_vers', '-productVersion'])
                name = self.run_command(['sw_vers', '-productName'])
                if version and name:
                    return f"{name} {version}"
                return f"macOS {platform.release()}"
                
            elif system == "Windows":
                wmic_os = self.run_command('wmic os get Caption,Version /value')
                if wmic_os:
                    caption = None
                    version = None
                    for line in wmic_os.split('\n'):
                        if 'Caption=' in line and line.split('=')[1].strip():
                            caption = line.split('=')[1].strip()
                        elif 'Version=' in line and line.split('=')[1].strip():
                            version = line.split('=')[1].strip()
                    
                    if caption and version:
                        return f"{caption} (Version {version})"
                    elif caption:
                        return caption
                
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    
                    try:
                        display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                        product_name = winreg.QueryValueEx(key, "ProductName")[0]
                        build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                        
                        if int(build) >= 22000:
                            product_name = product_name.replace("Windows 10", "Windows 11")
                        
                        return f"{product_name} {display_version} (Build {build})"
                    except:
                        product_name = winreg.QueryValueEx(key, "ProductName")[0]
                        build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                        
                        if int(build) >= 22000:
                            product_name = product_name.replace("Windows 10", "Windows 11")
                        
                        return f"{product_name} (Build {build})"
                except:
                    pass
                
                return f"Windows {platform.release()}"
            else:
                return f"{system} {platform.release()}"
        except:
            return "Unknown OS"
    
    def get_kernel(self):
        try:
            system = platform.system()
            if system == "Linux":
                return platform.release()
            elif system == "Darwin":
                return f"Darwin {platform.release()}"
            elif system == "Windows":
                return f"NT {platform.version()}"
            else:
                return platform.release()
        except:
            return "Unknown"
    
    def get_uptime(self):
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime = timedelta(seconds=int(uptime_seconds))
            
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            parts = []
            if days > 0:
                parts.append(f"{days}d")
            if hours > 0:
                parts.append(f"{hours}h")
            if minutes > 0:
                parts.append(f"{minutes}m")
            
            return " ".join(parts) if parts else "0m"
        except:
            return "Unknown"
    
    def get_packages(self):
        try:
            counts = []
            
            managers = [
                ('apt', ['dpkg', '--get-selections'], lambda x: len([l for l in x.split('\n') if '\tinstall' in l])),
                ('dnf/yum', ['rpm', '-qa'], lambda x: len(x.split('\n'))),
                ('pacman', ['pacman', '-Q'], lambda x: len(x.split('\n'))),
                ('portage', ['qlist', '-I'], lambda x: len(x.split('\n'))),
                ('xbps', ['xbps-query', '-l'], lambda x: len(x.split('\n'))),
                ('apk', ['apk', 'info'], lambda x: len(x.split('\n'))),
                ('brew', ['brew', 'list'], lambda x: len(x.split('\n'))),
                ('pip', ['pip', 'list'], lambda x: len(x.split('\n')) - 2 if len(x.split('\n')) > 2 else 0),
                ('conda', ['conda', 'list'], lambda x: len([l for l in x.split('\n') if l and not l.startswith('#')])),
                ('npm', ['npm', 'list', '-g', '--depth=0'], lambda x: len([l for l in x.split('\n') if '├──' in l or '└──' in l])),
                ('gem', ['gem', 'list'], lambda x: len(x.split('\n'))),
                ('cargo', ['cargo', 'install', '--list'], lambda x: len([l for l in x.split('\n') if l and not l.startswith(' ')]))
            ]
            
            for name, cmd, counter in managers:
                output = self.run_command(cmd)
                if output:
                    try:
                        count = counter(output)
                        if count > 0:
                            counts.append(f"{count} ({name})")
                    except:
                        continue
            
            return ", ".join(counts[:3]) if counts else "Unknown"  
        except:
            return "Unknown"
    
    def get_shell(self):
        try:
            shell_path = os.environ.get('SHELL', '')
            if shell_path:
                shell_name = os.path.basename(shell_path)
                version = self.run_command([shell_name, '--version'])
                if version:
                    version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version.split('\n')[0])
                    if version_match:
                        return f"{shell_name} {version_match.group(1)}"
                return shell_name
            else:
                if platform.system() == "Windows":
                    return "PowerShell" if "powershell" in os.environ.get('PSModulePath', '').lower() else "cmd"
            return "Unknown"
        except:
            return "Unknown"
    
    def get_desktop(self):
        try:
            de_vars = [
                'XDG_CURRENT_DESKTOP',
                'DESKTOP_SESSION',
                'XDG_SESSION_DESKTOP',
                'CURRENT_DESKTOP'
            ]
            
            for var in de_vars:
                de = os.environ.get(var)
                if de:
                    return de
            
            if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return 'GNOME'
            elif os.environ.get('KDE_FULL_SESSION'):
                return 'KDE'
            elif os.environ.get('MATE_DESKTOP_SESSION_ID'):
                return 'MATE'
            elif os.environ.get('XFCE4_SESSION'):
                return 'XFCE4'
            
            try:
                processes = [p.name() for p in psutil.process_iter(['name'])]
                if 'gnome-shell' in processes:
                    return 'GNOME'
                elif 'kwin' in processes or 'plasmashell' in processes:
                    return 'KDE'
                elif 'xfwm4' in processes:
                    return 'XFCE4'
                elif 'marco' in processes:
                    return 'MATE'
                elif 'openbox' in processes:
                    return 'Openbox'
            except:
                pass
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_window_manager(self):
        try:
            wm = os.environ.get('WINDOW_MANAGER')
            if wm:
                return os.path.basename(wm)
            
            wms = ['i3', 'bspwm', 'awesome', 'dwm', 'openbox', 'fluxbox', 'jwm']
            try:
                processes = [p.name() for p in psutil.process_iter(['name'])]
                for wm in wms:
                    if wm in processes:
                        return wm
            except:
                pass
                
            return None
        except:
            return None
    
    def get_cpu(self):
        try:
            cpu_info = ""
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            if platform.system() == "Linux":
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'model name' in line:
                                cpu_info = line.split(':')[1].strip()
                                break
                except:
                    pass
            elif platform.system() == "Darwin":
                cpu_info = self.run_command(['sysctl', '-n', 'machdep.cpu.brand_string'])
            elif platform.system() == "Windows":
                cpu_info = self.run_command('wmic cpu get name /value').split('=')[1] if self.run_command('wmic cpu get name /value') else ""
            
            if not cpu_info:
                cpu_info = platform.processor()
            
            cpu_info = re.sub(r'\s+', ' ', cpu_info)
            cpu_info = cpu_info.replace('(R)', '').replace('(TM)', '').replace('CPU', '').replace('@', '').strip()
            
            if cpu_count != cpu_count_logical:
                cpu_info += f" ({cpu_count}C/{cpu_count_logical}T)"
            else:
                cpu_info += f" ({cpu_count}C)"
                
            return cpu_info
        except:
            return "Unknown CPU"
    
    def get_gpu(self):
        try:
            gpus = []
            
            if platform.system() == "Linux":
                lspci = self.run_command(['lspci'])
                if lspci:
                    for line in lspci.split('\n'):
                        if 'VGA' in line or 'Display' in line or '3D' in line:
                            gpu = line.split(': ')[-1]
                            gpus.append(gpu)
                
                nvidia = self.run_command(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'])
                if nvidia:
                    gpus.extend(nvidia.split('\n'))
                    
            elif platform.system() == "Windows":
                wmic = self.run_command('wmic path win32_VideoController get name /value')
                if wmic:
                    for line in wmic.split('\n'):
                        if 'Name=' in line and line.split('=')[1].strip():
                            gpus.append(line.split('=')[1].strip())
                            
            elif platform.system() == "Darwin":
                system_profiler = self.run_command(['system_profiler', 'SPDisplaysDataType'])
                if system_profiler:
                    for line in system_profiler.split('\n'):
                        if 'Chipset Model:' in line:
                            gpu = line.split(':')[1].strip()
                            gpus.append(gpu)
            
            return gpus[0] if gpus else "Unknown"
        except:
            return "Unknown"
    
    def get_memory(self):
        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024**3)
            total_gb = mem.total / (1024**3)
            return f"{used_gb:.1f}GB / {total_gb:.1f}GB ({mem.percent:.0f}%)"
        except:
            return "Unknown"
    
    def get_swap(self):
        try:
            swap = psutil.swap_memory()
            if swap.total > 0:
                used_gb = swap.used / (1024**3)
                total_gb = swap.total / (1024**3)
                percent = (swap.used / swap.total * 100) if swap.total > 0 else 0
                return f"{used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.0f}%)"
            return "Not configured"
        except:
            return "Unknown"
    
    def get_disk(self):
        try:
            if platform.system() == "Windows":
                disk = psutil.disk_usage('C:')
            else:
                disk = psutil.disk_usage('/')
            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)
            percent = (disk.used / disk.total) * 100
            return f"{used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.0f}%)"
        except:
            return "Unknown"
    
    def get_network(self):
        try:
            interfaces = psutil.net_if_addrs()
            active_interfaces = []
            
            for interface, addresses in interfaces.items():
                if interface == 'lo' or interface.startswith('docker'):
                    continue
                for addr in addresses:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        active_interfaces.append(f"{interface} ({addr.address})")
                        break
            
            return ", ".join(active_interfaces[:2]) if active_interfaces else "Unknown"
        except:
            return "Unknown"
    
    def get_resolution(self):
        try:
            if platform.system() == "Linux":
                xrandr = self.run_command(['xrandr', '--current'])
                if xrandr:
                    resolutions = []
                    for line in xrandr.split('\n'):
                        if '*' in line and 'x' in line:
                            match = re.search(r'(\d+x\d+)', line)
                            if match:
                                resolutions.append(match.group(1))
                    return ", ".join(set(resolutions)) if resolutions else "Unknown"
                
                xdpyinfo = self.run_command(['xdpyinfo'])
                if xdpyinfo:
                    for line in xdpyinfo.split('\n'):
                        if 'dimensions:' in line:
                            match = re.search(r'(\d+x\d+)', line)
                            if match:
                                return match.group(1)
                                
            elif platform.system() == "Windows":
                wmic = self.run_command('wmic desktopmonitor get screenheight,screenwidth /value')
                if wmic:
                    width = height = None
                    for line in wmic.split('\n'):
                        if 'ScreenWidth=' in line:
                            width = line.split('=')[1].strip()
                        elif 'ScreenHeight=' in line:
                            height = line.split('=')[1].strip()
                    if width and height and width != '0':
                        return f"{width}x{height}"
                        
            elif platform.system() == "Darwin":
                system_profiler = self.run_command(['system_profiler', 'SPDisplaysDataType'])
                if system_profiler:
                    for line in system_profiler.split('\n'):
                        if 'Resolution:' in line:
                            match = re.search(r'(\d+\s*x\s*\d+)', line)
                            if match:
                                return match.group(1).replace(' ', '')
            
            return "Unknown"
        except:
            return "Unknown"
    
    def get_terminal(self):
        try:
            term_vars = ['TERM_PROGRAM', 'TERMINAL_EMULATOR', 'TERM']
            for var in term_vars:
                term = os.environ.get(var)
                if term and term not in ['xterm', 'xterm-256color', 'screen']:
                    return term
            
            try:
                ppid = os.getppid()
                parent = psutil.Process(ppid)
                parent_name = parent.name()
                
                terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'mate-terminal', 
                           'terminator', 'tilix', 'alacritty', 'kitty', 'urxvt', 'xterm',
                           'iTerm', 'Terminal', 'WindowsTerminal', 'ConEmu']
                
                for term in terminals:
                    if term.lower() in parent_name.lower():
                        return term
                        
                return parent_name
            except:
                pass
                
            return os.environ.get('TERM', 'Unknown')
        except:
            return "Unknown"
    
    def get_battery(self):
        try:
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    status = "Charging" if battery.power_plugged else "Discharging"
                    return f"{battery.percent:.0f}% ({status})"
            
            if platform.system() == "Linux":
                upower = self.run_command(['upower', '-i', '/org/freedesktop/UPower/devices/BAT0'])
                if upower:
                    percent = None
                    state = None
                    for line in upower.split('\n'):
                        if 'percentage' in line.lower():
                            percent = line.split(':')[-1].strip()
                        elif 'state' in line.lower():
                            state = line.split(':')[-1].strip()
                    if percent and state:
                        return f"{percent} ({state})"
                
                try:
                    bat_path = "/sys/class/power_supply/BAT0/"
                    if os.path.exists(bat_path):
                        with open(bat_path + "capacity", 'r') as f:
                            capacity = f.read().strip()
                        with open(bat_path + "status", 'r') as f:
                            status = f.read().strip()
                        return f"{capacity}% ({status})"
                except:
                    pass
            
            return "Not available"
        except:
            return "Not available"
    
    def get_temperature(self):
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    cpu_temps = []
                    for name, entries in temps.items():
                        if 'coretemp' in name.lower() or 'cpu' in name.lower():
                            for entry in entries:
                                if entry.current:
                                    cpu_temps.append(entry.current)
                    if cpu_temps:
                        avg_temp = sum(cpu_temps) / len(cpu_temps)
                        return f"{avg_temp:.1f}°C"
            
            if platform.system() == "Linux":
                try:
                    thermal_zones = [f for f in os.listdir('/sys/class/thermal/') if f.startswith('thermal_zone')]
                    for zone in thermal_zones:
                        try:
                            with open(f'/sys/class/thermal/{zone}/temp', 'r') as f:
                                temp = int(f.read().strip()) / 1000
                                return f"{temp:.1f}°C"
                        except:
                            continue
                except:
                    pass
                
                sensors = self.run_command(['sensors'])
                if sensors:
                    for line in sensors.split('\n'):
                        if 'Core 0' in line or 'CPU Temperature' in line:
                            temp_match = re.search(r'(\d+\.\d+)°C', line)
                            if temp_match:
                                return f"{temp_match.group(1)}°C"
            
            return "Not available"
        except:
            return "Not available"
    
    def get_load_average(self):
        try:
            if hasattr(os, 'getloadavg'):
                load1, load5, load15 = os.getloadavg()
                return f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
            elif platform.system() == "Linux":
                with open('/proc/loadavg', 'r') as f:
                    load_data = f.read().strip().split()
                    return f"{load_data[0]}, {load_data[1]}, {load_data[2]}"
            return "Not available"
        except:
            return "Not available"
    
    def get_processes(self):
        try:
            return str(len(psutil.pids()))
        except:
            return "Unknown"
    
    def get_users(self):
        try:
            users = psutil.users()
            if users:
                user_list = []
                for user in users:
                    user_info = f"{user.name}"
                    if hasattr(user, 'terminal') and user.terminal:
                        user_info += f" ({user.terminal})"
                    user_list.append(user_info)
                return ", ".join(set(user_list))
            return "None"
        except:
            return "Unknown"
    
    def get_ip_address(self):
        try:
            services = [
                'https://api.ipify.org',
                'https://ipinfo.io/ip',
                'https://ident.me'
            ]
            
            for service in services:
                try:
                    with urllib.request.urlopen(service, timeout=3) as response:
                        ip = response.read().decode('utf-8').strip()
                        if ip and '.' in ip:
                            return ip
                except:
                    continue
            
            return "Not available"
        except:
            return "Not available"
    
    def get_disk_usage_all(self):
        try:
            partitions = psutil.disk_partitions()
            disk_info = []
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    used_gb = usage.used / (1024**3)
                    total_gb = usage.total / (1024**3)
                    percent = (usage.used / usage.total) * 100
                    
                    mount_point = partition.mountpoint
                    if platform.system() == "Windows":
                        mount_point = partition.device
                    
                    disk_info.append(f"{mount_point}: {used_gb:.1f}GB/{total_gb:.1f}GB ({percent:.0f}%)")
                except (PermissionError, OSError):
                    continue
            
            return " | ".join(disk_info[:3]) if disk_info else "Unknown"
        except:
            return "Unknown"
    
    def get_architecture(self):
        try:
            return platform.machine() or platform.architecture()[0]
        except:
            return "Unknown"
    
    def get_hostname_info(self):
        try:
            hostname = socket.gethostname()
            try:
                fqdn = socket.getfqdn()
                if fqdn != hostname and '.' in fqdn:
                    return f"{hostname} ({fqdn})"
            except:
                pass
            return hostname
        except:
            return "Unknown"
    
    def get_timezone(self):
        try:
            if platform.system() == "Linux":
                try:
                    with open('/etc/timezone', 'r') as f:
                        return f.read().strip()
                except:
                    pass
                
                timedatectl = self.run_command(['timedatectl', 'show', '--property=Timezone', '--value'])
                if timedatectl:
                    return timedatectl
                
                localtime = self.run_command(['readlink', '/etc/localtime'])
                if localtime and 'zoneinfo' in localtime:
                    return localtime.split('zoneinfo/')[-1]
            
            elif platform.system() == "Darwin":
                timezone = self.run_command(['systemsetup', '-gettimezone'])
                if timezone:
                    return timezone.replace('Time Zone: ', '')
            
            elif platform.system() == "Windows":
                timezone = self.run_command('tzutil /g')
                if timezone:
                    return timezone
            
            import time
            return time.tzname[0]
        except:
            return "Unknown"
    
    def get_python_version(self):
        try:
            return f"Python {platform.python_version()}"
        except:
            return "Unknown"
    
    def get_session_info(self):
        try:
            session_info = []
            
            session_type = os.environ.get('XDG_SESSION_TYPE', '')
            if session_type:
                session_info.append(f"Type: {session_type}")
            
            if os.environ.get('WAYLAND_DISPLAY'):
                session_info.append("Wayland")
            elif os.environ.get('DISPLAY'):
                session_info.append("X11")
            
            return " | ".join(session_info) if session_info else "Unknown"
        except:
            return "Unknown"
    
    def get_ascii_art(self):
        system = platform.system().lower()
        
        if "linux" in system:
            return [
                f"{self.colors['blue']}                   -`{self.colors['end']}",
                f"{self.colors['blue']}                  .o+`{self.colors['end']}",
                f"{self.colors['blue']}                 `ooo/{self.colors['end']}",
                f"{self.colors['blue']}                `+oooo:{self.colors['end']}",
                f"{self.colors['blue']}               `+oooooo:{self.colors['end']}",
                f"{self.colors['blue']}               -+oooooo+:{self.colors['end']}",
                f"{self.colors['blue']}             `/:-:++oooo+:{self.colors['end']}",
                f"{self.colors['blue']}            `/++++/+++++++:{self.colors['end']}",
                f"{self.colors['blue']}           `/++++++++++++++:{self.colors['end']}",
                f"{self.colors['blue']}          `/+++ooooooooo+/`{self.colors['end']}",
                f"{self.colors['blue']}         ./ooosssso++osssssso+`{self.colors['end']}",
                f"{self.colors['blue']}        .oossssso-````/ossssss+`{self.colors['end']}",
                f"{self.colors['blue']}       -osssssso.      :ssssssso.{self.colors['end']}",
                f"{self.colors['blue']}      :osssssss/        osssso+++.{self.colors['end']}",
                f"{self.colors['blue']}     /ossssssss/        +ssssooo/-{self.colors['end']}",
                f"{self.colors['blue']}   `/ossssso+/:-        -:/+osssso+-{self.colors['end']}",
                f"{self.colors['blue']}  `+sso+:-`                 `.-/+oso:{self.colors['end']}",
                f"{self.colors['blue']} `++:.                           `-/+/{self.colors['end']}",
                f"{self.colors['blue']} .`                                 `/{self.colors['end']}"
            ]
        elif "darwin" in system:
            return [
                f"{self.colors['green']}                    'c.{self.colors['end']}",
                f"{self.colors['green']}                 ,xNMM.{self.colors['end']}",
                f"{self.colors['green']}               .OMMMMo{self.colors['end']}",
                f"{self.colors['green']}               OMMM0,{self.colors['end']}",
                f"{self.colors['green']}     .;loddo:' loolloddol;.{self.colors['end']}",
                f"{self.colors['green']}   cKMMMMMMMMMMNWMMMMMMMMMM0:{self.colors['end']}",
                f"{self.colors['yellow']} .KMMMMMMMMMMMMMMMMMMMMMMMWd.{self.colors['end']}",
                f"{self.colors['yellow']} XMMMMMMMMMMMMMMMMMMMMMMMX.{self.colors['end']}",
                f"{self.colors['red']};MMMMMMMMMMMMMMMMMMMMMMMM:{self.colors['end']}",
                f"{self.colors['red']}:MMMMMMMMMMMMMMMMMMMMMMMM:{self.colors['end']}",
                f"{self.colors['red']}.MMMMMMMMMMMMMMMMMMMMMMMMX.{self.colors['end']}",
                f"{self.colors['purple']} kMMMMMMMMMMMMMMMMMMMMMMMMWd.{self.colors['end']}",
                f"{self.colors['purple']} .XMMMMMMMMMMMMMMMMMMMMMMMMMMk{self.colors['end']}",
                f"{self.colors['blue']}  .XMMMMMMMMMMMMMMMMMMMMMMMMK.{self.colors['end']}",
                f"{self.colors['blue']}    kMMMMMMMMMMMMMMMMMMMMMMd{self.colors['end']}",
                f"{self.colors['cyan']}     ;KMMMMMMMWXXWMMMMMMMk.{self.colors['end']}",
                f"{self.colors['cyan']}       .cooc,.    .,coo:.{self.colors['end']}"
            ]
        elif "windows" in system:
            return [
        f"{self.colors['blue']}        ██████████████████████████{self.colors['end']}",
        f"{self.colors['blue']}        ██████████████████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['blue']}        ███████████{self.colors['cyan']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ███████████{self.colors['yellow']}█████████████{self.colors['end']}",
        f"{self.colors['green']}        ██████████████████████████{self.colors['end']}",
        f"{self.colors['green']}        ██████████████████████████{self.colors['end']}"            ]
        else:
            return [
                f"{self.colors['cyan']}     .-\"\"\"\"\"-. {self.colors['end']}",
                f"{self.colors['cyan']}   .'          '. {self.colors['end']}",
                f"{self.colors['cyan']}  /   O      O   \\ {self.colors['end']}",
                f"{self.colors['cyan']} :                : {self.colors['end']}",
                f"{self.colors['cyan']} |                | {self.colors['end']}",
                f"{self.colors['cyan']} :       __       : {self.colors['end']}",
                f"{self.colors['cyan']}  \\  .-\"`  `\"-.  / {self.colors['end']}",
                f"{self.colors['cyan']}   '.          .' {self.colors['end']}",
                f"{self.colors['cyan']}     '-.......-' {self.colors['end']}",
                "",
                f"{self.colors['bold']}   Unknown System{self.colors['end']}"
            ]
    def gather_info(self):
        info_functions = {
            'hostname': self.get_hostname_info,
            'os': self.get_os_info,
            'kernel': self.get_kernel,
            'architecture': self.get_architecture,
            'uptime': self.get_uptime,
            'packages': self.get_packages,
            'shell': self.get_shell,
            'desktop': self.get_desktop,
            'window_manager': self.get_window_manager,
            'terminal': self.get_terminal,
            'cpu': self.get_cpu,
            'gpu': self.get_gpu,
            'memory': self.get_memory,
            'swap': self.get_swap,
            'disk': self.get_disk,
            'network': self.get_network,
            'resolution': self.get_resolution,
            'battery': self.get_battery,
            'temperature': self.get_temperature,
            'load_average': self.get_load_average,
            'processes': self.get_processes,
            'users': self.get_users,
            'ip_address': self.get_ip_address,
            'timezone': self.get_timezone,
            'python_version': self.get_python_version,
            'session': self.get_session_info
        }
        
        for key, func in info_functions.items():
            try:
                self.info[key] = func()
            except Exception as e:
                self.info[key] = "Error"
    
    def format_info_line(self, label, value, color='white'):
        if value and value != "Unknown" and value != "Error" and value != "Not available":
            return f"{self.colors[color]}{label}:{self.colors['end']} {value}"
        return None
    
    def display(self):
        self.gather_info()
        
        ascii_art = self.get_ascii_art()
        
        info_lines = []
        
        username = getpass.getuser()
        hostname = self.info.get('hostname', 'unknown')
        info_lines.append(f"{self.colors['green']}{self.colors['bold']}{username}@{hostname}{self.colors['end']}")
        info_lines.append(f"{self.colors['green']}{'-' * len(f'{username}@{hostname}')}{self.colors['end']}")
        
        info_items = [
            ('OS', self.info.get('os'), 'blue'),
            ('Kernel', self.info.get('kernel'), 'cyan'),
            ('Architecture', self.info.get('architecture'), 'yellow'),
            ('Uptime', self.info.get('uptime'), 'green'),
            ('Packages', self.info.get('packages'), 'purple'),
            ('Shell', self.info.get('shell'), 'red'),
            ('Desktop', self.info.get('desktop'), 'blue'),
            ('Terminal', self.info.get('terminal'), 'cyan'),
            ('CPU', self.info.get('cpu'), 'yellow'),
            ('GPU', self.info.get('gpu'), 'green'),
            ('Memory', self.info.get('memory'), 'purple'),
            ('Swap', self.info.get('swap'), 'red'),
            ('Disk', self.info.get('disk'), 'blue'),
            ('Network', self.info.get('network'), 'cyan'),
            ('Resolution', self.info.get('resolution'), 'yellow'),
            ('Battery', self.info.get('battery'), 'green'),
            ('Temperature', self.info.get('temperature'), 'purple'),
            ('Load Avg', self.info.get('load_average'), 'red'),
            ('Processes', self.info.get('processes'), 'blue'),
            ('Users', self.info.get('users'), 'cyan'),
            ('Public IP', self.info.get('ip_address'), 'yellow'),
            ('Timezone', self.info.get('timezone'), 'green'),
            ('Python', self.info.get('python_version'), 'purple'),
            ('Session', self.info.get('session'), 'red')
        ]
        
        for label, value, color in info_items:
            line = self.format_info_line(label, value, color)
            if line:
                info_lines.append(line)
        
        ascii_width = 35
        max_lines = max(len(ascii_art), len(info_lines))
        
        print()
        
        for i in range(max_lines):
            if i < len(ascii_art):
                ascii_line = ascii_art[i]
                ascii_clean = re.sub(r'\033\[[0-9;]*m', '', ascii_line)
                ascii_padding = ascii_width - len(ascii_clean)
                ascii_formatted = ascii_line + (' ' * ascii_padding)
            else:
                ascii_formatted = ' ' * ascii_width
            
            if i < len(info_lines):
                info_line = info_lines[i]
            else:
                info_line = ""
            
            print(f"{ascii_formatted}  {info_line}")
        
        print()
    
    def display_compact(self):
        self.gather_info()
        
        username = getpass.getuser()
        hostname = self.info.get('hostname', 'unknown')
        
        print(f"\n{self.colors['bold']}{self.colors['green']}{username}@{hostname}{self.colors['end']}")
        print("=" * (len(username) + len(hostname) + 1))
        
        categories = {
            "System": [
                ('OS', self.info.get('os')),
                ('Kernel', self.info.get('kernel')),
                ('Architecture', self.info.get('architecture')),
                ('Uptime', self.info.get('uptime'))
            ],
            "Software": [
                ('Packages', self.info.get('packages')),
                ('Shell', self.info.get('shell')),
                ('Desktop', self.info.get('desktop')),
                ('Terminal', self.info.get('terminal'))
            ],
            "Hardware": [
                ('CPU', self.info.get('cpu')),
                ('GPU', self.info.get('gpu')),
                ('Memory', self.info.get('memory')),
                ('Disk', self.info.get('disk'))
            ],
            "Network": [
                ('Local IP', self.info.get('network')),
                ('Public IP', self.info.get('ip_address')),
                ('Resolution', self.info.get('resolution'))
            ],
            "Status": [
                ('Battery', self.info.get('battery')),
                ('Temperature', self.info.get('temperature')),
                ('Load Avg', self.info.get('load_average')),
                ('Processes', self.info.get('processes'))
            ]
        }
        
        for category, items in categories.items():
            print(f"\n{self.colors['bold']}{category}:{self.colors['end']}")
            for label, value in items:
                if value and value not in ["Unknown", "Error", "Not available"]:
                    print(f"  {self.colors['cyan']}{label}:{self.colors['end']} {value}")

def main():
    fetch = metafetch()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("MetaFetch - System Information Tool")
            print("Usage:")
            print("  metafetch         - Display full output with ASCII art")
            print("  metafetch -c      - Display compact output")
            print("  metafetch --help  - Show this help message")
            return
        elif sys.argv[1] in ['-c', '--compact']:
            fetch.display_compact()
            return
    
    fetch.display()

if __name__ == "__main__":
    main()
