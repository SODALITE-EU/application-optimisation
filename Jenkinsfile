pipeline {
    agent { label 'docker-slave' }
       environment {
       // OPENSTACK SETTINGS
       ssh_key_name = "jenkins-modak"
       image_name = "centos7"
       network_name = "orchestrator-network"
       security_groups = "default,sodalite-remote-access,sodalite-rest,sodalite-uc"
       flavor_name = "m1.small"
       // DOCKER SETTINGS
       docker_network = "sodalite"
       dockerhub_user = " "
       dockerhub_pass = " "
       docker_registry_ip = credentials('jenkins-docker-registry-ip')
       docker_registry_cert_country_name = "DE"
       docker_registry_cert_organization_name = "HLRS"
       docker_public_registry_url = "registry.hub.docker.com"
       docker_registry_cert_email_address = "steven.presser@hlrs.de"
       cert_path = "/home/modak/certs"
       cert_files_prefix = "image.docker.local"

       // OIDC secrets
       oidc_endpoint = credentials('oidc-endpoint')
       oidc_secret = credentials('oidc-secret')
       auth_api_key = credentials('auth-api-key')
       // VAULT
       vault_url = credentials('vault-url')
       // GIT SETTINGS
       git_type = "gitlab"
       git_server_url = "https://gitlab.com"
       git_auth_token = credentials('git-auth-token')
       // OPENSTACK DEPLOYMENT FALLBACK SETTINGS
       OS_PROJECT_DOMAIN_NAME = "Default"
       OS_USER_DOMAIN_NAME = "Default"
       OS_PROJECT_NAME = "orchestrator"
       OS_TENANT_NAME = "orchestrator"
       OS_USERNAME = credentials('os-username')
       OS_PASSWORD = credentials('os-password')
       OS_AUTH_URL = credentials('os-auth-url')
       OS_INTERFACE = "public"
       OS_IDENTITY_API_VERSION = "3"
       OS_REGION_NAME = "RegionOne"
       OS_AUTH_PLUGIN = "password"
       // ANSIBLE SETTINGS
       ANSIBLE_TIMEOUT = "60"

       // CI-CD vars
       // When triggered from git tag, $BRANCH_NAME is actually GIT's tag_name
       TAG_SEM_VER_COMPLIANT = """${sh(
                returnStdout: true,
                script: './validate_tag.sh SemVar $BRANCH_NAME'
            )}"""

       TAG_MAJOR_RELEASE = """${sh(
                returnStdout: true,
                script: './validate_tag.sh MajRel $BRANCH_NAME'
            )}"""

       TAG_PRODUCTION = """${sh(
                returnStdout: true,
                script: './validate_tag.sh production $BRANCH_NAME'
            )}"""

       TAG_STAGING = """${sh(
                returnStdout: true,
                script: './validate_tag.sh staging $BRANCH_NAME'
            )}"""
   }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Inspect GIT TAG'){
            steps {
                sh """ #!/bin/bash
                echo 'TAG: $BRANCH_NAME'
                echo 'Tag is compliant with SemVar 2.0.0: $TAG_SEM_VER_COMPLIANT'
                echo 'Tag is Major release: $TAG_MAJOR_RELEASE'
                echo 'Tag is production: $TAG_PRODUCTION'
                echo 'Tag is staging: $TAG_STAGING'
                """
            }

        }
        stage('Test MODAK') {
            steps {
                sh  """ #!/bin/bash
                docker-compose down || :
                if [ -n "\$(docker ps | grep modak)" ]; then
                    docker kill \$(docker ps | grep modak | awk '{print \$1}') || :
                fi
                docker-compose build --no-cache
                docker-compose up -d
                sleep 300 # MODAK won't be able to conenct to mysql without a wait. Might be more sane to check if mysql is ready, but this will do for now
                #docker exec \$(docker ps | grep modak | grep restapi | awk '{print \$1}') /bin/bash -c "cd ../test; python3 -m unittest -v"
                RES=\$?
                docker-compose down
                exit \$RES
                    """
                //docker-compose build --no-cache
                //docker-compose up -d
                //docker exec -it applicationoptimisation_restapi_1 /bin/bash -c "cd ../test; python3 -m unittest -v"
                //RES=\$?
                //docker-compose down
                //exit \$RES
                // python3 -m venv venv-test
                // . venv-test/bin/activate
                // python3 -m pip install --upgrade pip
                // python3 -m pip install --no-cache-dir -r MODAK/requirements.txt
                // cd MODAK/test
                //junit 'src/results.xml'
                //# Running tests in this envornment doesn't work yet.
                //#PYTHONPATH=${PYTHONPATH}:../src python3 -m pytest --junitxml=../results.xml --cov=../MODAK
            }
        }
        stage('SonarQube analysis'){
            environment {
            scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh  """ #!/bin/bash
                            ${scannerHome}/bin/sonar-scanner
                        """
                }
            }
        }
        stage('Build modak') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                sh """#!/bin/bash
                    cd MODAK
                    ../make_docker.sh build modak
                    """
            }
        }
        stage('Push modak to sodalite-private-registry') {
            // Push during staging and production
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                        ./make_docker.sh push modak staging
                        """
                }
            }
        }
        stage('Push modak to DockerHub') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push modak production
                        """
                }
            }
        }
        stage('Install deploy dependencies') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                sh """#!/bin/bash
                   """
            }
        }
        stage('Deploy to openstack for staging') {
            // Only on staging tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true'
                    }
                }
            }
            environment {
                // add env var for this stage only
                vm_name = 'modak-dev'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'modak_ssh_key', keyFileVariable: 'modak_ssh_key_file', usernameVariable: 'modak_ssh_username')]) {
                    sh """#!/bin/bash
                        hostname
                        ls
                        ssh -i ${modak_ssh_key_file} -o StrictHostKeyChecking=no ${modak_ssh_username}@192.168.2.155 "cd application-optimization && docker-compose down && cd .. && rm -rf application-optimization; docker kill \$(docker ps | grep modak | awk '{print \$1}'); mkdir -p application-optimization"
                        scp -i ${modak_ssh_key_file} -r ./* ${modak_ssh_username}@192.168.2.155:application-optimization/
                        ssh -i ${modak_ssh_key_file} -o StrictHostKeyChecking=no ${modak_ssh_username}@192.168.2.155 "cd application-optimization && docker-compose up -d"
                        sleep 100
                        ssh -i ${modak_ssh_key_file} -o StrictHostKeyChecking=no ${modak_ssh_username}@192.168.2.155 "docker ps; echo docker exec \\\$(docker ps | grep modak | grep restapi | awk '{print \\\$1}' ) ../test/integration/hpc.sh; docker exec \$(docker ps | grep modak | grep restapi | awk '{print \$1}' ) ../test/integration/hpc.sh"
                       """
                        //docker pull \${docker_registry_ip:-localhost}/modak-api:$BRANCH_NAME
                        //docker-compose up -d
                        //docker exec -it applicationoptimisation_restapi_1 /bin/bash -c "cd ../test; python3 -m unittest -v"
                        //RES=\$?
                        //exit \$RES
                }
            }
        }
        stage('Deploy to openstack for production') {
            // Only on production tags
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            environment {
                vm_name = 'modak'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'modak_ssh_key', keyFileVariable: 'modak_ssh_key_file', usernameVariable: 'modak_ssh_username')]) {
                    sh """#!/bin/bash
                       """
                }
            }
        }

    }
}
