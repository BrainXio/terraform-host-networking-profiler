# Host Networking Profiler Module Overview

This module collects non-sensitive networking details from the host machine where Terraform is executed. It uses a Python script to detect whether a wired or wireless network interface has a public (non-RFC1918) IP address, proxy settings (http_proxy, https_proxy, no_proxy without credentials), and interface information (name, type as wired/wireless/overlay, status as up/down, CIDR if non-private), outputting the results as a JSON object saved to `network_profile.json`. Sensitive data (e.g., private IPs, proxy credentials) is explicitly excluded to prevent leaks.

## Purpose
The module provides a reusable way to profile the networking environment for inventory, auditing, or configuration purposes in infrastructure-as-code workflows.
