#!powershell
# This file is part of Ansible
#
# Copyright 2018, Jimmy Conner <jconner@redhat.com>
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# WANT_JSON
# POWERSHELL_COMMON

$params = Parse-Args $args -supports_check_mode $true

$suffixes = (Get-AnsibleParam -obj $params -name "suffixes" -type "list" -failifempty $true) -join ","
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false

$result = @{
    changed = $false
    msg = ""
}

try {
    $current = ((Get-DnsClientGlobalSetting | Select SuffixSearchList).SuffixSearchList) -join ","
    if ($suffixes -eq $current) {
        $result.msg = "Suffixes are present"
    } else {
        if (-not $check_mode) {
            Set-DnsClientGlobalSetting -SuffixSearchList $suffixes
        }
        $result.changed = $true
        $result.msg = "Updated Suffixes: Original: ($current) -- New: ($suffixes)"
    }
}
catch {
    Fail-Json $result $_.Exception.Message
}

Exit-Json $result