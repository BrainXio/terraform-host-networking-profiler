## Additional Notes

- Requires Python 3.x on the host; the `netifaces` library is optional for enhanced interface detection but not required.
- The module supports Linux, Windows, and macOS hosts. Networking details are detected using standard Python libraries (`os`, `subprocess`, `urllib.parse`) and optional `netifaces`.
- Adjust `python_interpreter` if the Python 3 executable has a different name (e.g., `python`).
- The JSON output is a flattened map with string values to comply with Terraform's `external` data source requirements (e.g., `{"has_public_ip": "false", "http_proxy": "http://proxy.example.com:8080", "interfaces_eth0_type": "wired", "interfaces_eth0_status": "up", "interfaces_wlan0_type": "wireless", "interfaces_wlan0_status": "down", "interfaces_tailscale0_type": "overlay", "interfaces_tailscale0_status": "up"}`).
- Fields are included only if detected; otherwise, they are omitted:
  - `has_public_ip`: True if a wired or wireless NIC has a non-RFC1918 IP (excludes overlay networks like Tailscale, ZeroTier); false otherwise.
  - `http_proxy`, `https_proxy`: Proxy URLs without usernames or passwords if set.
  - `no_proxy`: List of hosts excluded from proxying if set.
  - `interfaces_<name>_type`: `wired` (e.g., eth*, en*), `wireless` (e.g., wlan*, wl*), or `overlay` (e.g., tailscale*, zt*).
  - `interfaces_<name>_status`: `up` or `down` based on interface state.
  - `interfaces_<name>_cidr`: Network CIDR if available and non-private (excludes RFC1918 IPs).
- No sensitive data (e.g., private RFC1918 IPs, MAC addresses, proxy credentials) is collected to ensure security.
- Detection methods:
  - Public IP: Checks wired/wireless NICs via `netifaces` (if available), excluding RFC1918, private IPv6 (ULA, link-local), and overlay interfaces.
  - Proxy: Reads `http_proxy`, `https_proxy`, `no_proxy` environment variables, stripping credentials from proxy URLs.
  - Interfaces: Uses `netifaces` or system commands (`ip addr`, `ifconfig`, `ipconfig`). Loopback interfaces (`lo`, `lo0`) are excluded.
  - Status: Uses `/sys/class/net` or `ip link` (Linux), `netsh` (Windows), or `ifconfig` (macOS).
- Overlay networks (e.g., Tailscale, ZeroTier) are identified by interface names (`tailscale*`, `zt*`, `wg*`, `tun*`, `tap*`) and marked as `overlay`.
- Generate documentation with `make docs`, which runs `terraform-docs` with headers and footers from `docs/`.
- CI/CD is handled by GitHub Actions workflows (`.github/workflows/lint.yml` for linting and `.github/workflows/validate.yml` for validation).
- See `examples/simple/README.md` for a basic usage example of the module.
- If unexpected files (e.g., `project.json`) appear, ensure they are excluded in `.gitignore` or manually removed before committing.

## Resources
- [Terraform External Data Source](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external)
- [Terraform Local Provider](https://registry.terraform.io/providers/hashicorp/local/latest/docs)
