import jenkins.model.*
import hudson.security.*

def instance = Jenkins.getInstance()

def authStrategy = instance.getAuthorizationStrategy()

if (authStrategy instanceof GlobalMatrixAuthorizationStrategy) {
    def strategy = (GlobalMatrixAuthorizationStrategy) authStrategy

    def permissionsToAdd = [
        Jenkins.READ,
        View.READ,
        Job.READ
    ]

    permissionsToAdd.each { perm ->
        if (!strategy.getGrantedPermissions()[perm]?.contains("anonymous")) {
            strategy.add(perm, "anonymous")
            println "Added permission: ${perm.group.title} → ${perm.name} for anonymous"
        } else {
            println "Permission already exists: ${perm.group.title} → ${perm.name} for anonymous"
        }
    }

    instance.setAuthorizationStrategy(strategy)
    instance.save()
    println "Permissions updated successfully."
} else {
    println "Current authorization strategy is not Matrix-based. Aborting."
}