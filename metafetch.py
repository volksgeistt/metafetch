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
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                    build = winreg.QueryValueEx(key, "CurrentBuild")[0]
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
                f"{self.colors['blue']}        ,.=:!!t3Z3z.,{self.colors['end']}",
                f"{self.colors['blue']}       :tt:::tt333EE3{self.colors['end']}",
                f"{self.colors['blue']}       Et:::ztt33EEEL{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['cyan']} @@@@@@@@@@@@@@@@@@@@{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['end']}",
                f"{self.colors['blue']}       Et:::zt333EEE{self.colors['end']}"
            ]
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
    
    def collect_info(self):
        self.info = {
            'user': getpass.getuser(),
            'hostname': socket.gethostname(),
            'os': self.get_os_info(),
            'kernel': self.get_kernel(),
            'uptime': self.get_uptime(),
            'packages': self.get_packages(),
            'shell': self.get_shell(),
            'desktop': self.get_desktop(),
            'wm': self.get_window_manager(),
            'terminal': self.get_terminal(),
            'cpu': self.get_cpu(),
            'gpu': self.get_gpu(),
            'memory': self.get_memory(),
            'swap': self.get_swap(),
            'disk': self.get_disk(),
            'network': self.get_network(),
            'resolution': self.get_resolution()
        }
    
    def display(self):
        self.collect_info()
        ascii_art = self.get_ascii_art()
        
        user_host = f"{self.colors['bold']}{self.colors['green']}{self.info['user']}{self.colors['red']}@{self.colors['blue']}{self.info['hostname']}{self.colors['end']}"
        separator = f"{self.colors['gray']}{'-' * (len(self.info['user']) + len(self.info['hostname']) + 1)}{self.colors['end']}"
        
        info_lines = [
            user_host,
            separator,
            f"{self.colors['bold']}{self.colors['red']}OS{self.colors['end']}: {self.info['os']}",
            f"{self.colors['bold']}{self.colors['yellow']}Kernel{self.colors['end']}: {self.info['kernel']}",
            f"{self.colors['bold']}{self.colors['green']}Uptime{self.colors['end']}: {self.info['uptime']}",
            f"{self.colors['bold']}{self.colors['blue']}Packages{self.colors['end']}: {self.info['packages']}",
            f"{self.colors['bold']}{self.colors['purple']}Shell{self.colors['end']}: {self.info['shell']}",
            f"{self.colors['bold']}{self.colors['cyan']}Desktop{self.colors['end']}: {self.info['desktop']}",
        ]
        
        if self.info['wm'] and self.info['wm'].lower() not in self.info['desktop'].lower():
            info_lines.append(f"{self.colors['bold']}{self.colors['white']}WM{self.colors['end']}: {self.info['wm']}")
        
        info_lines.extend([
            f"{self.colors['bold']}{self.colors['red']}Terminal{self.colors['end']}: {self.info['terminal']}",
            f"{self.colors['bold']}{self.colors['yellow']}CPU{self.colors['end']}: {self.info['cpu']}",
            f"{self.colors['bold']}{self.colors['green']}GPU{self.colors['end']}: {self.info['gpu']}",
            f"{self.colors['bold']}{self.colors['blue']}Memory{self.colors['end']}: {self.info['memory']}"
        ])
        
        if self.info['swap'] != "Not configured":
            info_lines.append(f"{self.colors['bold']}{self.colors['purple']}Swap{self.colors['end']}: {self.info['swap']}")
        
        info_lines.extend([
            f"{self.colors['bold']}{self.colors['cyan']}Disk{self.colors['end']}: {self.info['disk']}",
f"{self.colors['white']}Network{self.colors['end']}: {self.info['network']}",
            f"{self.colors['bold']}{self.colors['gray']}Resolution{self.colors['end']}: {self.info['resolution']}"
        ])
        
        info_lines.append("")
        colors_line1 = ""
        colors_line2 = ""
        color_names = ['red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white', 'gray']
        
        for color in color_names:
            colors_line1 += f"{self.colors[color]}███{self.colors['end']}"
            colors_line2 += f"{self.colors[color]}███{self.colors['end']}"
        
        info_lines.extend([colors_line1, colors_line2])
        
        max_lines = max(len(ascii_art), len(info_lines))
        
        for i in range(max_lines):
            ascii_line = ascii_art[i] if i < len(ascii_art) else " " * 40
            info_line = info_lines[i] if i < len(info_lines) else ""
            
            clean_info = re.sub(r'\x1b\[[0-9;]*m', '', info_line)
            padding = " " * (3) 
            
            print(f"{ascii_line}{padding}{info_line}")
    
    def get_colors_demo(self):
        print("\nColor Palette:")
        for name, code in self.colors.items():
            if name != 'end':
                print(f"{code}{name.capitalize():10}{self.colors['end']}: {code}████████{self.colors['end']}")
    
    def get_minimal_info(self):
        return {
            'user_host': f"{getpass.getuser()}@{socket.gethostname()}",
            'os': platform.system(),
            'uptime': self.get_uptime(),
            'memory': self.get_memory()
        }
    
    def minimal_display(self):
        info = self.get_minimal_info()
        print(f"{self.colors['bold']}{self.colors['cyan']}{info['user_host']}{self.colors['end']}")
        print(f"{self.colors['yellow']}OS{self.colors['end']}: {info['os']}")
        print(f"{self.colors['green']}Uptime{self.colors['end']}: {info['uptime']}")
        print(f"{self.colors['blue']}Memory{self.colors['end']}: {info['memory']}")


def fetch(minimal=False, colors=False):
    pf = metafetch()
    
    if colors:
        pf.get_colors_demo()
    elif minimal:
        pf.minimal_display()
    else:
        pf.display()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='metafetch - Enhanced system information tool')
    parser.add_argument('-m', '--minimal', action='store_true', 
                       help='Display minimal information')
    parser.add_argument('-c', '--colors', action='store_true',
                       help='Display color palette')
    parser.add_argument('--version', action='version', version='metafetch 1.0.0')
    
    args = parser.parse_args()
    
    try:
        fetch(minimal=args.minimal, colors=args.colors)
    except KeyboardInterrupt:
        print(f"\n{metafetch().colors['red']}Interrupted by user{metafetch().colors['end']}")
        sys.exit(1)
    except Exception as e:
        print(f"{metafetch().colors['red']}Error: {e}{metafetch().colors['end']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
