import groovy.json.JsonSlurper
import org.sonatype.nexus.security.user.UserNotFoundException

parsed_args = new JsonSlurper().parseText(args)

try {
    // update an existing user
    user = security.securitySystem.getUser(parsed_args.username)
    user.setFirstName(parsed_args.first_name)
    user.setLastName(parsed_args.last_name)
    user.setEmailAddress(parsed_args.email)
    security.securitySystem.updateUser(user)
    security.setUserRoles(parsed_args.username, Eval.me(parsed_args.roles))
    security.securitySystem.changePassword(parsed_args.username, parsed_args.password)
} catch(UserNotFoundException ignored) {
    // create the new user
    security.addUser(parsed_args.username, parsed_args.first_name, parsed_args.last_name, parsed_args.email, true, parsed_args.password, Eval.me(parsed_args.roles))
}