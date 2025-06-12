import json
import platform
import os
import subprocess
import urllib.parse
try:
    import netifaces
except ImportError:
    netifaces = None

def is_rfc1918(ip):
    """Check if an IPv4 address is in RFC1918 private ranges."""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        nums = [int(p) for p in parts]
        return (nums[0] == 10 or
                (nums[0] == 172 and 16 <= nums[1] <= 31) or
                (nums[0] == 192 and nums[1] == 168))
    except (ValueError, IndexError):
        return False

def is_private_ipv6(ip):
    """Check if an IPv6 address is private (ULA or link-local)."""
    try:
        parts = ip.lower().split(':')
        if len(parts) < 1:
            return False
        first = parts[0]
        return first.startswith('fc') or first.startswith('fd') or first.startswith('fe80')
    except (ValueError, IndexError):
        return False

def is_public_ip(ip):
    """Check if an IP is public (non-RFC1918 for IPv4, non-private for IPv6)."""
    return not (is_rfc1918(ip) or is_private_ipv6(ip))

def strip_proxy_credentials(proxy_url):
    """Remove username and password from proxy URL."""
    try:
        parsed = urllib.parse.urlparse(proxy_url)
        if parsed.username or parsed.password:
            netloc = parsed.hostname
            if parsed.port:
                netloc += f":{parsed.port}"
            return urllib.parse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        return proxy_url
    except (ValueError, AttributeError):
        return proxy_url

def get_interface_type(iface_name):
    """Determine interface type: wired, wireless, or overlay."""
    iface_lower = iface_name.lower()
    overlay_patterns = ['tailscale', 'ts', 'zt', 'wg', 'tun', 'tap']
    if any(pattern in iface_lower for pattern in overlay_patterns):
        return 'overlay'
    wired_patterns = ['eth', 'en', 'ethernet']
    wireless_patterns = ['wlan', 'wl', 'wifi', 'wireless']
    if any(pattern in iface_lower for pattern in wired_patterns):
        return 'wired'
    if any(pattern in iface_lower for pattern in wireless_patterns):
        return 'wireless'
    return 'wired'  # Default to wired for unknown interfaces

def is_loopback(iface_name):
    """Check if an interface is loopback."""
    return iface_name.lower() in ['lo', 'lo0', 'localhost']

def get_interface_status(iface_name, system):
    """Check if an interface is up and active."""
    try:
        if system == "linux":
            try:
                with open(f"/sys/class/net/{iface_name}/operstate", 'r') as f:
                    state = f.read().strip().lower()
                    return 'up' if state == 'up' else 'down'
            except (IOError, FileNotFoundError):
                result = subprocess.run(['ip', 'link', 'show', iface_name], capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'UP' in result.stdout:
                    return 'up'
                return 'down'
        elif system == "windows":
            result = subprocess.run(['netsh', 'interface', 'show', 'interface', iface_name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'Connected' in result.stdout:
                return 'up'
            return 'down'
        elif system == "darwin":
            result = subprocess.run(['ifconfig', iface_name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'status: active' in result.stdout.lower():
                return 'up'
            return 'down'
    except (subprocess.SubprocessError, FileNotFoundError):
        return 'down'

def get_network_info():
    network_info = {}
    try:
        # Proxy settings
        for proxy_var in ['http_proxy', 'https_proxy']:
            value = os.environ.get(proxy_var, '') or os.environ.get(proxy_var.upper(), '')
            if value:
                network_info[proxy_var] = strip_proxy_credentials(value)
        if os.environ.get('no_proxy', '') or os.environ.get('NO_PROXY', ''):
            network_info['no_proxy'] = os.environ.get('no_proxy', '') or os.environ.get('NO_PROXY', '')
        # Network interfaces
        if netifaces:
            has_public_ip = False
            system = platform.system().lower()
            for iface in netifaces.interfaces():
                if is_loopback(iface):
                    continue
                try:
                    iface_key = f"interfaces_{iface.replace(':', '_')}"
                    iface_type = get_interface_type(iface)
                    iface_info = {'type': iface_type}
                    # Interface status
                    iface_info['status'] = get_interface_status(iface, system)
                    # Check for public IP (IPv4/IPv6)
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs and iface_type != 'overlay':
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr.get('addr', '')
                            if ip and is_public_ip(ip):
                                has_public_ip = True
                    if netifaces.AF_INET6 in addrs and iface_type != 'overlay':
                        for addr in addrs[netifaces.AF_INET6]:
                            ip = addr.get('addr', '').split('%')[0]
                            if ip and is_public_ip(ip):
                                has_public_ip = True
                    # CIDR (subnet)
                    cidr = ''
                    if system == "linux":
                        try:
                            result = subprocess.run(['ip', 'addr', 'show', iface], capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                for line in result.stdout.splitlines():
                                    if 'inet ' in line and '/' in line:
                                        ip_cidr = line.split()[1]
                                        if not is_rfc1918(ip_cidr.split('/')[0]):
                                            cidr = ip_cidr
                                            break
                        except (subprocess.SubprocessError, FileNotFoundError):
                            pass
                    elif system == "windows":
                        try:
                            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                iface_found = False
                                for line in result.stdout.splitlines():
                                    if iface in line:
                                        iface_found = True
                                    if iface_found and 'IPv4 Address' in line:
                                        ip = line.split(':')[1].strip()
                                        if not is_rfc1918(ip):
                                            mask_line = next((l for l in result.stdout.splitlines() if 'Subnet Mask' in l), None)
                                            if mask_line:
                                                mask = mask_line.split(':')[1].strip()
                                                if mask:
                                                    cidr = f"{ip}/{mask_to_cidr(mask)}"
                                                    break
                        except (subprocess.SubprocessError, FileNotFoundError):
                            pass
                    elif system == "darwin":
                        try:
                            result = subprocess.run(['ifconfig', iface], capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                for line in result.stdout.splitlines():
                                    if 'inet ' in line and '/' in line:
                                        ip_cidr = line.split()[1]
                                        if not is_rfc1918(ip_cidr.split('/')[0]):
                                            cidr = ip_cidr
                                            break
                        except (subprocess.SubprocessError, FileNotFoundError):
                            pass
                    if cidr:
                        iface_info['cidr'] = cidr
                    network_info.update({f"{iface_key}_{k}": v for k, v in iface_info.items()})
                except Exception:
                    pass
            network_info['has_public_ip'] = str(has_public_ip).lower()
        else:
            network_info['has_public_ip'] = 'false'
    except Exception:
        pass
    return {k: v for k, v in network_info.items() if v}

def mask_to_cidr(mask):
    """Convert subnet mask to CIDR prefix length."""
    try:
        return sum(bin(int(x)).count('1') for x in mask.split('.'))
    except (ValueError, AttributeError):
        return ''

def main():
    profile = get_network_info()
    print(json.dumps(profile))

if __name__ == "__main__":
    main()
