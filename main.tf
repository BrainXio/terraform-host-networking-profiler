data "external" "network_profile" {
  program = [var.python_interpreter, "${path.module}/files/network_profile.py"]
}

resource "local_file" "network_output" {
  content  = jsonencode(data.external.network_profile.result)
  filename = "${path.cwd}/network_profile.json"
}
