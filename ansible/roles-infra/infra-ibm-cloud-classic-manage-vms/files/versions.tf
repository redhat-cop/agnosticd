terraform {
  required_version = ">= 1.0"
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = "~> 1.60"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
} 