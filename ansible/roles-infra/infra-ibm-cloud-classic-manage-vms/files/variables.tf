variable "ibm_cloud_api_key" {
  description = "IBM Cloud API key"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "IBM Cloud region"
  type        = string
  default     = "us-south"
}

variable "guid" {
  description = "Unique identifier for the deployment"
  type        = string
}

variable "domain" {
  description = "Domain name for VMs"
  type        = string
  default     = "iaas.rhdp.net"
}

variable "image" {
  description = "Default image for VMs"
  type        = string
  default     = "REDHAT_9_64"
}

variable "network_speed" {
  description = "Network speed in Mbps"
  type        = number
  default     = 1000
}

variable "hourly_billing" {
  description = "Use hourly billing"
  type        = bool
  default     = true
}

variable "private_network_only" {
  description = "Use private network only"
  type        = bool
  default     = false
}

variable "cores" {
  description = "Default number of CPU cores"
  type        = number
  default     = 2
}

variable "memory" {
  description = "Default memory in MB"
  type        = number
  default     = 4096
}

variable "rootfs_size" {
  description = "Default root filesystem size in GB"
  type        = number
  default     = 25
}

variable "additional_disks" {
  description = "Default additional disks"
  type        = list(number)
  default     = []
}

variable "local_disk" {
  description = "Use local disk"
  type        = bool
  default     = true
}

variable "ssh_key_ids" {
  description = "Default SSH key IDs"
  type        = list(string)
  default     = []
}

variable "user_metadata" {
  description = "Default user metadata"
  type        = string
  default     = ""
}

variable "notes" {
  description = "Default notes for VMs"
  type        = string
  default     = "VM created by AgnosticD"
}

variable "dedicated_acct_host_only" {
  description = "Use dedicated account host only"
  type        = bool
  default     = false
}

variable "private_vlan_id" {
  description = "Private VLAN ID"
  type        = string
  default     = ""
}

variable "public_vlan_id" {
  description = "Public VLAN ID"
  type        = string
  default     = ""
}

variable "post_install_script_uri" {
  description = "Post-installation script URI"
  type        = string
  default     = ""
}



variable "instances" {
  description = "VM instances configuration"
  type = list(object({
    name           = string
    datacenter     = string
    count          = number
    cores          = optional(number)
    memory         = optional(number)
    rootfs_size    = optional(number)
    additional_disks = optional(list(number))
    image          = optional(string)
    ssh_key_ids    = optional(list(string))
    user_metadata  = optional(string)
    notes          = optional(string)
    tags           = optional(list(string))
    private_security_group_rules = optional(list(object({
      name        = string
      description = string
      rule_type   = string
      ether_type  = string
      from_port   = optional(number)
      to_port     = optional(number)
      protocol    = string
      cidr        = string
    })), [])
    public_security_group_rules = optional(list(object({
      name        = string
      description = string
      rule_type   = string
      ether_type  = string
      from_port   = optional(number)
      to_port     = optional(number)
      protocol    = string
      cidr        = string
    })), [])
  }))
}

variable "total_vm_count" {
  description = "Total number of VMs to create"
  type        = number
} 