// -------------- Configuration --------------
// CloudForms
def opentlc_creds = 'b93d2da4-c2b7-45b5-bf3b-ee2c08c6368e'
def opentlc_admin_creds = '73b84287-8feb-478a-b1f2-345fd0a1af47'
def cf_uri = 'https://rhpds.redhat.com'
def cf_group = 'rhpds-access-cicd'
// IMAP
def imap_creds = 'd8762f05-ca66-4364-adf2-bc3ce1dca16c'
def imap_server = 'imap.gmail.com'
// Notifications
def notification_email = 'gpteinfrasev3@redhat.com'
def rocketchat_hook = '5d28935e-f7ca-4b11-8b8e-d7a7161a013a'

// state variables
def guid=''
def openshift_location = ''

// Catalog items
def choices = [
    'DevOps Shared Cluster Development / DEV - IOT Enterprise 4.0 Demo',
    'IoT Demos / IoT Industry 4.0 Demo',
].join("\n")

pipeline {
    agent any

    parameters {
        booleanParam(
            defaultValue: false,
            description: 'wait for user input before deleting the environment',
                name: 'confirm_before_delete'
        )
        choice(
            choices: choices,
            description: 'Catalog item',
            name: 'catalog_item',
        )
    }

    options {
        buildDiscarder(logRotator(daysToKeepStr: '30'))
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
                git 'https://github.com/redhat-gpte-devopsautomation/cloudforms-oob'

                script {
                    def catalog = params.catalog_item.split(' / ')[0].trim()
                    def item = params.catalog_item.split(' / ')[1].trim()
                    def cfparams = [
                        'status=t',
                        'check=t',
                        'quotacheck=t',
                        "region=global_gpte",
                        'expiration=7',
                        'runtime=8',
                        'users=2',
                        'nodes=2',
                    ].join(',').trim()
                    echo "'${catalog}' '${item}'"
                    guid = sh(
                        returnStdout: true,
                        script: """
                          ./opentlc/order_svc_guid.sh \
                          -c '${catalog}' \
                          -i '${item}' \
                          -G '${cf_group}' \
                          -d '${cfparams}'
                        """
                    ).trim()

                    echo "GUID is '${guid}'"
                }
            }
        }

        stage('Wait for last email and parse OpenShift location') {
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
                          --filter 'has completed'
                        """
                    ).trim()


                    def m = email =~ /You can find the master's console here: ([^ <]+)/
                    openshift_location = m[0][1]
                }
            }
        }

        stage('Test OpenShift access') {
            environment {
                credentials = credentials("${opentlc_creds}")
            }
            steps {
                sh "./tests/jenkins/downstream/openshift_client.sh '${openshift_location}'"
            }
        }

        stage('Test demo') {
            options {
                timeout(time: 20, unit: 'MINUTES')
            }
            environment {
                credentials = credentials("${opentlc_creds}")
            }
            steps {
                sh "./tests/jenkins/downstream/openshift_test_demo.sh '${openshift_location}' '${guid}'"
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
                git url: 'https://github.com/redhat-cop/agnosticd',
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
        stage('Ensure projects are deleted') {
            steps {
                withCredentials([usernameColonPassword(credentialsId: opentlc_creds, variable: 'credentials')]) {
                    sh "./tests/jenkins/downstream/openshift_ensure_projects_deleted.sh '${openshift_location}' '${guid}'"
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
