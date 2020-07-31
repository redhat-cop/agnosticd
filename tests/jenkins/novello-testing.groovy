// -------------- Configuration --------------
// CloudForms
def opentlc_creds = 'b93d2da4-c2b7-45b5-bf3b-ee2c08c6368e'
def opentlc_admin_creds = '73b84287-8feb-478a-b1f2-345fd0a1af47'
def cf_uri = 'https://labs.opentlc.com'
def cf_group = 'opentlc-access-cicd'
// IMAP
def imap_creds = 'd8762f05-ca66-4364-adf2-bc3ce1dca16c'
def imap_server = 'imap.gmail.com'
// Notifications
def notification_email = 'gpteinfrasev3@redhat.com'
def rocketchat_hook = '5d28935e-f7ca-4b11-8b8e-d7a7161a013a'

// SSH key
def ssh_creds = '15e1788b-ed3c-4b18-8115-574045f32ce4'

// Admin host ssh location is in a credential too
def ssh_admin_host = 'admin-host-na'

// state variables
def guid=''
def external_host = ''


// Catalog items
def catalog_choices = [
    'Novello Testing',
].join("\n")

// Catalog items
def catalog_item_choices = [
    'N-3scale API Mgmt & Service Mesh',
    'N-3scale API Mgmt & Service Mesh',
    'N-3scale OCP VM AI',
    'N-AI OCP VM',
    'N-AMQ OCP VM',
    'N-AMQ Online Foundations',
    'N-AMQ Streams Foundations',
    'N-Ansible Advanced - OpenStack',
    'N-Ansible Tower Implementation 3.3',
    'N-App Migration to OCP',
    'N-cee-cf-110',
    'N-cee-sf-016',
    'N-CloudForms 4.5 Foundations Lab',
    'N-Decision Manager 7 Experienced',
    'N-Decision Manager 7 Foundations',
    'N-EAP 7 Development',
    'N-Gluster Storage 3.1 Foundations Lab',
    'N-HANA scaleout internal',
    'N-MSA Orchestration using PAM 7',
    'N-OpenStack 10 Concepts and Architecture',
    'N-OpenStack 10 Implementation',
    'N-OpenStack 12 Implementation',
    'N-OpenStack 13 Implementation',
    'N-OpenStack Advanced Networking',
    'N-OSP16 HA  (Overcloud installed)',
    'N-PAM 7: Advanced',
    'N-PAM 7: Case Management',
    'N-PAM 7: Foundations',
    'N-Red Hat Ceph Storage 2.0 Foundations',
    'N-Red Hat Virtualization 4 Imp',
    'N-RHEL 7 Implementation Lab',
    'N-RHEL 7 Troubleshooting Lab',
    'N-RHEL 8 New Features For Exp. Admins',
    'N-RHSUMMIT20: OCP4.3 ON OSP16',
    'N-RHTE19: Dynamic Case Mgmt',
    'N-RHTE19: E2E API Lifecycle Mgmt',
    'N-RHTE19: Emergency Response Quarkus',
    'N-RHTE19: Quarkus / Kogito',
    'N-RHV 4.0 Foundations Lab',
    'N-Satellite 6.2 Foundations lab',
    'N-Satellite 6.5 Implementation Lab',
    'N-Satellite 6 Foundations Lab',
    'N-Satellite 6 Implementation Lab',
    'N-TEST OpenShift 4 Config Lab (OSP)',
].join("\n")

def region_choice = [
    'NA - DEV',
    'EMEA - DEV',
    'APAC - DEV',
    'NA',
    'EMEA',
    'APAC',
].join("\n")

def environment_choice = [
    'DEV',
    'TEST',
    'PROD',
].join("\n")

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
    }

    parameters {
        booleanParam(
            defaultValue: false,
            description: 'wait for user input before deleting the environment',
                name: 'confirm_before_delete'
        )
        choice(
            choices: catalog_choices,
            description: 'Catalog',
            name: 'catalog',
        )
        choice(
            choices: catalog_item_choices,
            description: 'Catalog item',
            name: 'catalog_item',
        )
        choice(
            choices: region_choice,
            description: 'Catalog item',
            name: 'region',
        )
        choice(
            choices: environment_choice,
            description: 'Environment',
            name: 'environment',
        )
    }

    stages {
        stage('order from CF') {
            environment {
                uri = "${cf_uri}"
                credentials = credentials("${opentlc_creds}")
                DEBUG = 'true'
            }
            /* This step use the order_svc_guid.sh script to order
             a service from CloudForms */
            steps {
                git url: 'https://github.com/redhat-gpte-devopsautomation/cloudforms-oob'

                script {
                    def catalog = params.catalog.trim()
                    def item = params.catalog_item.trim()
                    def region = params.region.trim()
                    def environment = params.environment.trim()
                    def cfparams = [
                        'status=t',
                        'check=t',
                        'check2=t',
                        'expiration=2',
                        'runtime=10',
                        'quotacheck=t',
                        "region=${region}",
                        "environment=${environment}",
                    ].join(',').trim()

                    echo "'${catalog}' '${item}'"
                    guid = sh(
                        returnStdout: true,
                        script: """
                          ./opentlc/order_svc_guid.sh \
                          -c '${catalog}' \
                          -i '${item}' \
                          -G '${cf_group}' \
                          -d '${cfparams}' \
                        """
                    ).trim()

                    echo "GUID is '${guid}'"
                }
            }
        }

        // This kind of CI send only one mail
        stage('Wait to receive and parse email') {
            environment {
                credentials=credentials("${imap_creds}")
            }
            steps {
                git url: 'https://github.com/redhat-cop/agnosticd',
                    branch: 'development'

                script {
                    email = sh(
                        returnStdout: true,
                        script: """
                          ./tests/jenkins/downstream/poll_email.py \
                          --server '${imap_server}' \
                          --guid ${guid} \
                          --timeout 30 \
                          --filter 'is building'
                        """
                    ).trim()

                    try {
                    	def m = email =~ /External Hostname<\/TH><TD>(.*)/
                    	def mm = email =~ /(.*)<\/TD><\/TR><TR><TH>Internal Hostname/
                    	external_host = m[0][1].replaceAll("=","") + mm[0][1].replaceAll(" ","")
                    	echo "External-Host='${external_host}'"
                    } catch(Exception ex) {
                        echo "Could not parse email:"
                        echo email
                        echo ex.toString()
                        throw ex
                    }
                }
            }
        }
        
        stage ('Wait to complete provision') {
        	steps {
				echo "Wait for 30 minutes for deployment to complete"
				sleep 1800 // seconds
			}
		}

        stage('Confirm before retiring') {
            when {
                expression {
                    return params.confirm_before_delete
                }
            }
            steps {
                input "Continue ?"
            }
        }
        stage('Retire service from CF') {
            environment {
                uri = "${cf_uri}"
                credentials = credentials("${opentlc_creds}")
                admin_credentials = credentials("${opentlc_admin_creds}")
                DEBUG = 'true'
            }
            /* This step uses the delete_svc_guid.sh script to retire
             the service from CloudForms */
            steps {
                git 'https://github.com/redhat-gpte-devopsautomation/cloudforms-oob'

                sh "./opentlc/delete_svc_guid.sh '${guid}'"
            }
            post {
                failure {
                    withCredentials([usernameColonPassword(credentialsId: imap_creds, variable: 'credentials')]) {
                        mail(
                            subject: "${env.JOB_NAME} (${env.BUILD_NUMBER}) failed retiring for GUID=${guid}",
                            body: "It appears that ${env.BUILD_URL} is failing, somebody should do something about that.\nMake sure GUID ${guid} is destroyed.",
                            to: "${notification_email}",
                            replyTo: "${notification_email}",
                            from: credentials.split(':')[0]
                        )
                    }
                    withCredentials([string(credentialsId: rocketchat_hook, variable: 'HOOK_URL')]) {
                        sh(
                            """
                            curl -H 'Content-Type: application/json' \
                            -X POST '${HOOK_URL}' \
                            -d '{\"username\": \"jenkins\", \"icon_url\": \"https://dev-sfo01.opentlc.com/static/81c91982/images/headshot.png\", \"text\": \"@here :rage: ${env.JOB_NAME} (${env.BUILD_NUMBER}) failed retiring ${guid}.\"}'\
                            """.trim()
                        )
                    }
                }
            }
        }
        stage('Wait for deletion email') {
            steps {
                git url: 'https://github.com/sborenst/ansible_agnostic_deployer',
                    branch: 'development'

                withCredentials([usernameColonPassword(credentialsId: imap_creds, variable: 'credentials')]) {
                    sh """./tests/jenkins/downstream/poll_email.py \
                        --guid ${guid} \
                        --timeout 20 \
                        --server '${imap_server}' \
                        --filter 'has been deleted'"""
                }
            }
        }
    }

    post {
        failure {
            git 'https://github.com/redhat-gpte-devopsautomation/cloudforms-oob'
            /* retire in case of failure */
            withCredentials(
                [
                    usernameColonPassword(credentialsId: opentlc_creds, variable: 'credentials'),
                    usernameColonPassword(credentialsId: opentlc_admin_creds, variable: 'admin_credentials')
                ]
            ) {
                sh """
                export uri="${cf_uri}"
                export DEBUG=true
                ./opentlc/delete_svc_guid.sh '${guid}'
                """
            }

            /* Print ansible logs */
            withCredentials([
                string(credentialsId: ssh_admin_host, variable: 'ssh_admin'),
                sshUserPrivateKey(
                    credentialsId: ssh_creds,
                    keyFileVariable: 'ssh_key',
                    usernameVariable: 'ssh_username')
            ]) {
                sh("""
                    ssh -o StrictHostKeyChecking=no -i ${ssh_key} ${ssh_admin} \
                    "bin/logs.sh ${guid}" || true
                """.trim()
                )
            }

            withCredentials([usernameColonPassword(credentialsId: imap_creds, variable: 'credentials')]) {
                mail(
                    subject: "${env.JOB_NAME} (${env.BUILD_NUMBER}) failed GUID=${guid}",
                    body: "It appears that ${env.BUILD_URL} is failing, somebody should do something about that.",
                    to: "${notification_email}",
                    replyTo: "${notification_email}",
                    from: credentials.split(':')[0]
              )
            }
            withCredentials([string(credentialsId: rocketchat_hook, variable: 'HOOK_URL')]) {
                sh(
                    """
                      curl -H 'Content-Type: application/json' \
                      -X POST '${HOOK_URL}' \
                      -d '{\"username\": \"jenkins\", \"icon_url\": \"https://dev-sfo01.opentlc.com/static/81c91982/images/headshot.png\", \"text\": \"@here :rage: ${env.JOB_NAME} (${env.BUILD_NUMBER}) failed GUID=${guid}. It appears that ${env.BUILD_URL}/console is failing, somebody should do something about that.\"}'\
                    """.trim()
                )
            }
        }
        fixed {
            withCredentials([string(credentialsId: rocketchat_hook, variable: 'HOOK_URL')]) {
                sh(
                    """
                      curl -H 'Content-Type: application/json' \
                      -X POST '${HOOK_URL}' \
                      -d '{\"username\": \"jenkins\", \"icon_url\": \"https://dev-sfo01.opentlc.com/static/81c91982/images/headshot.png\", \"text\": \"@here :smile: ${env.JOB_NAME} is now FIXED, see ${env.BUILD_URL}/console\"}'\
                    """.trim()
                )
            }
        }
    }
}
