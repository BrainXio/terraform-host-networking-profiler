terraform {
  required_version = ">= 1.3.0"
}

module "network_profile" {
  source             = "../../"
  python_interpreter = "python3"
}

output "network_profile" {
  value = module.network_profile.network_profile
}

output "profile_file_path" {
  value = module.network_profile.profile_file_path
}
