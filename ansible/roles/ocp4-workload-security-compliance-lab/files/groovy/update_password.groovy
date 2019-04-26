import groovy.json.JsonSlurper

parsed_args = new JsonSlurper().parseText(args)

security.securitySystem.changePassword(parsed_args.username, parsed_args.new_password)