# Example: Basic Usage of brainxio/terraform-host-networking-profiler

## Overview
This example demonstrates how to use the `brainxio/terraform-host-networking-profiler` Terraform module to profile the networking environment on the host machine. The module generates a JSON file (`network_profile.json`) containing non-sensitive details such as whether a wired or wireless NIC has a public IP, proxy settings (without credentials), and interface information (type, status, non-private CIDR).

## Prerequisites
- Terraform >= 1.3.0
- Python 3.x installed on the host
- Optional: `netifaces` Python library for enhanced interface detection

## Usage
1. Navigate to the `examples/simple` directory:
   ```bash
   cd examples/simple
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Review the plan:
   ```bash
   terraform plan
   ```
4. Apply the configuration:
   ```bash
   terraform apply
   ```

This will execute the module, run the `network_profile.py` script, and generate `network_profile.json` in the current working directory.

## Example Output
- **File**: `network_profile.json` (e.g., `{"has_public_ip": "false", "http_proxy": "http://proxy.example.com:8080", "interfaces_eth0_type": "wired", "interfaces_eth0_status": "up", "interfaces_wlan0_type": "wireless", "interfaces_wlan0_status": "down"}`)
- **Terraform Outputs**:
  - `network_profile`: The JSON object with network details
  - `profile_file_path`: Path to `network_profile.json`

## Notes
- The `python_interpreter` variable defaults to `python3`. Adjust if your Python executable has a different name (e.g., `python`).
- Fields are included only if detected; private IPs (RFC1918) and proxy credentials are excluded for security.
- Overlay networks (e.g., Tailscale, ZeroTier) are marked as `overlay` and excluded from `has_public_ip`.
- This example is a reference for integrating the module into larger Terraform configurations. See the main module's documentation for advanced usage.
