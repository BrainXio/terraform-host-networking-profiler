<!-- BEGIN_TF_DOCS -->
# Host Networking Profiler Module Overview

This module collects non-sensitive networking details from the host machine where Terraform is executed. It uses a Python script to detect whether a wired or wireless network interface has a public (non-RFC1918) IP address, proxy settings (http\_proxy, https\_proxy, no\_proxy without credentials), and interface information (name, type as wired/wireless/overlay, status as up/down, CIDR if non-private), outputting the results as a JSON object saved to `network_profile.json`. Sensitive data (e.g., private IPs, proxy credentials) is explicitly excluded to prevent leaks.

## Purpose
The module provides a reusable way to profile the networking environment for inventory, auditing, or configuration purposes in infrastructure-as-code workflows.

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3.0 |
| <a name="requirement_external"></a> [external](#requirement\_external) | >= 2.2.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | >= 2.4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_external"></a> [external](#provider\_external) | >= 2.2.0 |
| <a name="provider_local"></a> [local](#provider\_local) | >= 2.4.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [local_file.network_output](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [external_external.network_profile](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_python_interpreter"></a> [python\_interpreter](#input\_python\_interpreter) | Python interpreter to use (e.g., 'python3') | `string` | `"python3"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_network_profile"></a> [network\_profile](#output\_network\_profile) | Network profile information as a flattened JSON object with string values, including whether a wired or wireless NIC has a public IP (non-RFC1918), proxy settings (http\_proxy, https\_proxy, no\_proxy without credentials), and interface details (name, type as wired/wireless/overlay, status as up/down, CIDR if non-private) |
| <a name="output_profile_file_path"></a> [profile\_file\_path](#output\_profile\_file\_path) | Path to the generated network profile JSON file |

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
<!-- END_TF_DOCS -->