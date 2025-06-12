output "network_profile" {
  description = "Network profile information as a flattened JSON object with string values, including whether a wired or wireless NIC has a public IP (non-RFC1918), proxy settings (http_proxy, https_proxy, no_proxy without credentials), and interface details (name, type as wired/wireless/overlay, status as up/down, CIDR if non-private)"
  value       = data.external.network_profile.result
}

output "profile_file_path" {
  description = "Path to the generated network profile JSON file"
  value       = local_file.network_output.filename
}
