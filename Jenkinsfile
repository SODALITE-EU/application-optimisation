pipeline {
    options {
        timeout(time: 3, unit: 'HOURS')   // timeout on whole pipeline job
        disableConcurrentBuilds()
    }
    agent { label 'docker-slave' }
       environment {
       // OPENSTACK SETTINGS
       ssh_key_name = "jenkins-opera"
       image_name = "centos7"
       username = "centos"
       network_name = "orchestrator-network"
       security_groups = "default,sodalite-remote-access,sodalite-rest,sodalite-uc"
       flavor_name = "m1.small"
       // DOCKER SETTINGS
       docker_network = "sodalite"
       dockerhub_user = " "
       dockerhub_pass = " "
       //docker_registry_ip = credentials('jenkins-docker-registry-ip')
       docker_registry_cert_country_name = "SI"
       docker_registry_cert_organization_name = "XLAB"
       docker_public_registry_url = "registry.hub.docker.com"
       docker_registry_cert_email_address = "dragan.radolovic@xlab.si"
       cert_path = "/home/xopera/certs"
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

       // ROOT X.509 CERTIFICATES
       ca_crt_file = credentials('xopera-ca-crt')
       ca_key_file = credentials('xopera-ca-key')

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
                sh  """ #!/bin/bash -l
                set -eux
                cd MODAK/

                python3 -m venv venv-pre-commit
                . venv-pre-commit/bin/activate
                python3 -m pip install --upgrade pip
                python3 -m pip install --no-cache-dir pre-commit
                pre-commit run -a
                """
                sh '''#! /bin/bash -l
                set -eux
                cd MODAK/

                # Remove any container left from a previous run first
                docker rm modak-unittest || :

                docker build -t modak-unittest .
                docker run --name modak-unittest modak-unittest pytest --cov-report xml:coverage.xml --junitxml=results.xml --cov=MODAK
                docker cp modak-unittest:/opt/app/results.xml results-docker.xml
                docker cp modak-unittest:/opt/app/coverage.xml coverage-docker.xml
                docker rm modak-unittest
                sed -i -e "s|/opt/app|$PWD|" coverage-docker.xml
                '''
                junit 'MODAK/results-*.xml'
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
                    ../make_docker.sh build modak-api
                    """
            }
        }
        stage('Push modak to DockerHub for staging') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true'
                    }
                }
            }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                        set -x
                        git status
                        ./make_docker.sh push modak-api sodaliteh2020 staging
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
                            ./make_docker.sh push modak-api sodaliteh2020 production
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
                    set -x
                    git status
                    rm -rf .venv
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python3 -m pip install --upgrade pip
                    python3 -m pip install -r deploy-requirements.txt
                    ansible-galaxy install geerlingguy.pip
                    ansible-galaxy install geerlingguy.docker
                    ansible-galaxy install geerlingguy.repo-epel
                    cp ${ca_crt_file} deploy-blueprint/modules/docker/artifacts/ca.crt
                    cp ${ca_crt_file} deploy-blueprint/modules/misc/tls/artifacts/ca.crt
                    cp ${ca_key_file} deploy-blueprint/modules/docker/artifacts/ca.key
                    cp ${ca_key_file} deploy-blueprint/modules/misc/tls/artifacts/ca.key
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
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        set -x
                        # create input.yaml file from template
                        envsubst < deploy-blueprint/input/input.yaml.tmpl > deploy-blueprint/input.yaml
                        . .venv/bin/activate
                        cd deploy-blueprint
                        rm -r -f .opera
                        ssh-keygen -f "/home/jenkins/.ssh/known_hosts" -R "77.231.202.232"

                        opera deploy service.yaml -i input.yaml
                    """
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
                vm_name = 'modak-prod'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        set -x
                        # create input.yaml file from template
                        envsubst < deploy-blueprint/input/input.yaml.tmpl > deploy-blueprint/input.yaml
                        . .venv/bin/activate
                        cd deploy-blueprint
                        rm -r -f .opera

                        opera deploy service.yaml -i input.yaml
                    """
                }
            }
        }

    }
}
