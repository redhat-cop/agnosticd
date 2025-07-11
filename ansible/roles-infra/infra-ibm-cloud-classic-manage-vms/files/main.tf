provider "ibm" {
  ibmcloud_api_key = var.ibm_cloud_api_key
  region           = var.region
}

# Private interface security groups
resource "ibm_security_group" "vm_private" {
  count = length([for vm in local.vm_list : vm if length(local.vm_private_rules[vm.name]) > 0])
  
  name = "${[for vm in local.vm_list : vm if length(local.vm_private_rules[vm.name]) > 0][count.index].name}-private-sg"
  description = "Private security group for ${[for vm in local.vm_list : vm if length(local.vm_private_rules[vm.name]) > 0][count.index].name}"
}

# Private interface security group rules
resource "ibm_security_group_rule" "vm_private_rules" {
  count = sum([for vm in local.vm_list : length(local.vm_private_rules[vm.name])])
  
  security_group_id = ibm_security_group.vm_private[local.private_rule_mapping[count.index].vm_index].id
  direction     = local.private_rule_mapping[count.index].rule.rule_type
  ether_type    = local.private_rule_mapping[count.index].rule.ether_type
  port_range_min = local.private_rule_mapping[count.index].rule.from_port != null ? local.private_rule_mapping[count.index].rule.from_port : null
  port_range_max = local.private_rule_mapping[count.index].rule.to_port != null ? local.private_rule_mapping[count.index].rule.to_port : null
  protocol      = local.private_rule_mapping[count.index].rule.protocol
  remote_ip     = local.private_rule_mapping[count.index].rule.cidr
}

# Public interface security groups
resource "ibm_security_group" "vm_public" {
  count = length([for vm in local.vm_list : vm if length(local.vm_public_rules[vm.name]) > 0])
  
  name = "${[for vm in local.vm_list : vm if length(local.vm_public_rules[vm.name]) > 0][count.index].name}-public-sg"
  description = "Public security group for ${[for vm in local.vm_list : vm if length(local.vm_public_rules[vm.name]) > 0][count.index].name}"
}

# Public interface security group rules
resource "ibm_security_group_rule" "vm_public_rules" {
  count = sum([for vm in local.vm_list : length(local.vm_public_rules[vm.name])])
  
  security_group_id = ibm_security_group.vm_public[local.public_rule_mapping[count.index].vm_index].id
  direction     = local.public_rule_mapping[count.index].rule.rule_type
  ether_type    = local.public_rule_mapping[count.index].rule.ether_type
  port_range_min = local.public_rule_mapping[count.index].rule.from_port != null ? local.public_rule_mapping[count.index].rule.from_port : null
  port_range_max = local.public_rule_mapping[count.index].rule.to_port != null ? local.public_rule_mapping[count.index].rule.to_port : null
  protocol      = local.public_rule_mapping[count.index].rule.protocol
  remote_ip     = local.public_rule_mapping[count.index].rule.cidr
}

# Local values for interface-specific security group logic
locals {
  # Private interface rules: only private-specific rules
  vm_private_rules = {
    for vm in local.vm_list : vm.name => vm.private_security_group_rules != null ? vm.private_security_group_rules : []
  }
  
  # Public interface rules: only public-specific rules  
  vm_public_rules = {
    for vm in local.vm_list : vm.name => vm.public_security_group_rules != null ? vm.public_security_group_rules : []
  }
  
  # Create mapping for private rule assignment
  private_rule_mapping = flatten([
    for vm_index, vm in local.vm_list : [
      for rule_index, rule in local.vm_private_rules[vm.name] : {
        vm_index = length([for v in slice(local.vm_list, 0, vm_index) : v if length(local.vm_private_rules[v.name]) > 0])
        rule     = rule
      }
    ] if length(local.vm_private_rules[vm.name]) > 0
  ])
  
  # Create mapping for public rule assignment
  public_rule_mapping = flatten([
    for vm_index, vm in local.vm_list : [
      for rule_index, rule in local.vm_public_rules[vm.name] : {
        vm_index = length([for v in slice(local.vm_list, 0, vm_index) : v if length(local.vm_public_rules[v.name]) > 0])
        rule     = rule
      }
    ] if length(local.vm_public_rules[vm.name]) > 0
  ])
}

# Virtual Server Instances
resource "ibm_compute_vm_instance" "vm" {
  count = var.total_vm_count
  
  hostname              = local.vm_hostnames[count.index]
  domain               = var.domain
  datacenter           = local.vm_datacenters[count.index]
  cores                = local.vm_cores[count.index]
  memory               = local.vm_memory[count.index]
  disks                = local.vm_disks[count.index]
  os_reference_code    = local.vm_images[count.index]
  local_disk           = var.local_disk
  network_speed        = var.network_speed
  hourly_billing       = var.hourly_billing
  private_network_only = var.private_network_only
  ssh_key_ids          = local.vm_ssh_key_ids[count.index]
  user_metadata        = local.vm_user_metadata[count.index]
  notes                = local.vm_notes[count.index]
  dedicated_acct_host_only = var.dedicated_acct_host_only
  tags                 = local.vm_tags[count.index]
  
  private_vlan_id = var.private_vlan_id != "" ? var.private_vlan_id : null
  public_vlan_id  = var.public_vlan_id != "" ? var.public_vlan_id : null
  
  post_install_script_uri = var.post_install_script_uri != "" ? var.post_install_script_uri : null
  
  # Security groups - apply interface-specific security groups
  private_security_group_ids = length(local.vm_private_rules[local.vm_list[count.index].name]) > 0 ? [ibm_security_group.vm_private[index([for vm in local.vm_list : vm.name if length(local.vm_private_rules[vm.name]) > 0], local.vm_list[count.index].name)].id] : []
  public_security_group_ids  = var.private_network_only ? [] : length(local.vm_public_rules[local.vm_list[count.index].name]) > 0 ? [ibm_security_group.vm_public[index([for vm in local.vm_list : vm.name if length(local.vm_public_rules[vm.name]) > 0], local.vm_list[count.index].name)].id] : []
}

# Local values for VM configuration
locals {
  # Flatten instances to individual VMs
  vm_list = flatten([
    for instance in var.instances : [
      for i in range(instance.count) : {
        name           = instance.count > 1 ? "${instance.name}-${format("%02d", i + 1)}" : instance.name
        instance_name  = instance.name
        datacenter     = instance.datacenter
        cores          = lookup(instance, "cores", var.cores)
        memory         = lookup(instance, "memory", var.memory)
        rootfs_size    = lookup(instance, "rootfs_size", var.rootfs_size)
        additional_disks = lookup(instance, "additional_disks", var.additional_disks)
        image          = lookup(instance, "image", var.image)
        ssh_key_ids    = lookup(instance, "ssh_key_ids", var.ssh_key_ids)
        user_metadata  = lookup(instance, "user_metadata", var.user_metadata)
        notes          = lookup(instance, "notes", var.notes)
        tags           = lookup(instance, "tags", [])
        private_security_group_rules = lookup(instance, "private_security_group_rules", [])
        public_security_group_rules = lookup(instance, "public_security_group_rules", [])
      }
    ]
  ])
  
  vm_hostnames = [for vm in local.vm_list : vm.name]
  vm_datacenters = [for vm in local.vm_list : vm.datacenter]
  vm_cores = [for vm in local.vm_list : vm.cores]
  vm_memory = [for vm in local.vm_list : vm.memory]
  vm_disks = [for vm in local.vm_list : concat([vm.rootfs_size], vm.additional_disks != null ? vm.additional_disks : [])]
  vm_images = [for vm in local.vm_list : vm.image]
  vm_ssh_key_ids = [for vm in local.vm_list : vm.ssh_key_ids]
  vm_user_metadata = [for vm in local.vm_list : vm.user_metadata]
  vm_notes = [for vm in local.vm_list : vm.notes]
  vm_tags = [for vm in local.vm_list : vm.tags]
}

# AWS Provider for Route53
provider "aws" {
  access_key = var.route53_aws_access_key_id
  secret_key = var.route53_aws_secret_access_key
  region     = var.aws_region
  
  # Only configure if we're creating DNS records
  skip_credentials_validation = !var.create_dns_records
  skip_metadata_api_check     = !var.create_dns_records
  skip_region_validation      = !var.create_dns_records
}

# Local values for DNS
locals {
  dns_domain = var.cluster_dns_zone != "" ? var.cluster_dns_zone : var.domain
}

# Route53 A records for public IPs
resource "aws_route53_record" "vm_public" {
  count = var.create_dns_records && !var.private_network_only ? length(ibm_compute_vm_instance.vm) : 0
  
  zone_id = var.route53_aws_zone_id
  name    = "${ibm_compute_vm_instance.vm[count.index].hostname}.${local.dns_domain}"
  type    = "A"
  ttl     = var.dns_ttl
  records = [ibm_compute_vm_instance.vm[count.index].ipv4_address]
  
  depends_on = [ibm_compute_vm_instance.vm]
}