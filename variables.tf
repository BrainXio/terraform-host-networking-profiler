variable "python_interpreter" {
  type        = string
  description = "Python interpreter to use (e.g., 'python3')"
  default     = "python3"
  validation {
    condition     = length(var.python_interpreter) > 0
    error_message = "Python interpreter cannot be empty"
  }
}
