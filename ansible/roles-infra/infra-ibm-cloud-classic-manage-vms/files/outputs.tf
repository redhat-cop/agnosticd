output "vm_count" {
  description = "Total number of VMs created"
  value       = var.total_vm_count
}

output "vm_ids" {
  description = "List of VM IDs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.id] : []
}

output "vm_hostnames" {
  description = "List of VM hostnames"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.hostname] : []
}

output "vm_domains" {
  description = "List of VM domains"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.domain] : []
}

output "vm_fqdns" {
  description = "List of VM FQDNs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : "${vm.hostname}.${vm.domain}"] : []
}

output "vm_public_ips" {
  description = "List of VM public IPs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.ipv4_address] : []
}

output "vm_private_ips" {
  description = "List of VM private IPs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.ipv4_address_private] : []
}

output "vm_datacenters" {
  description = "List of VM datacenters"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.datacenter] : []
}

output "vm_cores" {
  description = "List of VM CPU cores"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.cores] : []
}

output "vm_memory" {
  description = "List of VM memory in MB"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.memory] : []
}

output "vm_operating_systems" {
  description = "List of VM operating systems"
  value       = var.total_vm_count > 0 ? local.vm_images : []
}

output "vm_network_speeds" {
  description = "List of VM network speeds"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.network_speed] : []
}

output "vm_statuses" {
  description = "List of VM statuses"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : "active"] : []
}

output "ssh_connection_commands" {
  description = "List of SSH connection commands"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : "ssh root@${vm.ipv4_address}"] : []
}

output "private_security_group_ids" {
  description = "List of private security group IDs for each VM"
  value       = var.total_vm_count > 0 ? [for vm in local.vm_list : length(local.vm_private_rules[vm.name]) > 0 ? [ibm_security_group.vm_private[index([for v in local.vm_list : v.name if length(local.vm_private_rules[v.name]) > 0], vm.name)].id] : []] : []
}

output "public_security_group_ids" {
  description = "List of public security group IDs for each VM"
  value       = var.total_vm_count > 0 ? [for vm in local.vm_list : length(local.vm_public_rules[vm.name]) > 0 ? [ibm_security_group.vm_public[index([for v in local.vm_list : v.name if length(local.vm_public_rules[v.name]) > 0], vm.name)].id] : []] : []
}

output "vm_tags" {
  description = "List of VM tags"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.tags] : []
}

output "vm_hourly_billings" {
  description = "List of VM hourly billing settings"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.hourly_billing] : []
}

output "vm_creation_dates" {
  description = "List of VM creation dates"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : timestamp()] : []
}

output "private_vlan_ids" {
  description = "List of private VLAN IDs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.private_vlan_id] : []
}

output "public_vlan_ids" {
  description = "List of public VLAN IDs"
  value       = var.total_vm_count > 0 ? [for vm in ibm_compute_vm_instance.vm : vm.public_vlan_id] : []
}

output "vm_private_security_group_ids" {
  description = "Private security group IDs for each VM"
  value       = { for sg in ibm_security_group.vm_private : sg.name => sg.id }
}

output "vm_public_security_group_ids" {
  description = "Public security group IDs for each VM"
  value       = { for sg in ibm_security_group.vm_public : sg.name => sg.id }
}

output "deployment_summary" {
  description = "Deployment summary"
  value = {
    total_vms           = var.total_vm_count
    datacenters         = var.total_vm_count > 0 ? distinct([for vm in ibm_compute_vm_instance.vm : vm.datacenter]) : []
    total_cores         = var.total_vm_count > 0 ? sum([for vm in ibm_compute_vm_instance.vm : vm.cores]) : 0
    total_memory_mb     = var.total_vm_count > 0 ? sum([for vm in ibm_compute_vm_instance.vm : vm.memory]) : 0
    images_used         = var.total_vm_count > 0 ? distinct(local.vm_images) : []
    private_security_groups = length(ibm_security_group.vm_private)
    public_security_groups  = length(ibm_security_group.vm_public)
  }
}

# DNS outputs
output "dns_records_created" {
  description = "Whether DNS records were created"
  value       = var.create_dns_records
}

output "public_dns_names" {
  description = "Public DNS names created"
  value       = var.create_dns_records && var.total_vm_count > 0 ? [for record in aws_route53_record.vm_public : record.fqdn] : []
}

output "route53_zone_id" {
  description = "Route53 zone ID used"
  value       = var.create_dns_records ? var.route53_aws_zone_id : ""
}

output "cluster_dns_zone" {
  description = "DNS domain used for records"
  value       = var.create_dns_records ? local.dns_domain : ""
}

output "dns_connection_commands" {
  description = "SSH connection commands using DNS names"
  value       = var.create_dns_records && var.total_vm_count > 0 ? [for record in aws_route53_record.vm_public : "ssh root@${record.fqdn}"] : []
} 