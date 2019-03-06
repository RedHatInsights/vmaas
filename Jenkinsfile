/*
 * Pipeline for running integration tests in Jenkins job with 
 * every pull request or change in master
 *
 * Requires: https://github.com/RedHatInsights/insights-pipeline-lib
 */

@Library("github.com/RedHatInsights/insights-pipeline-lib") _

// Code coverage failure threshold
codecovThreshold = 89

node {
    // Cancel any prior builds that are running for this job
    cancelPriorBuilds()

    runStages()
}


def runStages() {
    // withNode is a helper to spin up a jnlp slave using the Kubernetes plugin, and run the body code on that slave
    openShift.withNode(image: "docker-registry.default.svc:5000/jenkins/jenkins-slave-vmaas:latest") {
        // check out source again to get it in this node"s workspace
        scmVars = checkout scm

        // checkout vmaas_tests git repository
        checkOutRepo(targetDir: "vmaas_tests", repoUrl: "https://github.com/RedHatInsights/vmaas_tests", credentialsId: "github")
        checkOutRepo(targetDir: "vmaas-yamls", repoUrl: "https://github.com/psegedy/vmaas-yamls", credentialsId: "github")

        stage("Pip install") {
            // withStatusContext runs the body code and notifies GitHub on whether it passed or failed
            withStatusContext.pipInstall {
                sh "pip install --user --no-warn-script-location -U pip devpi-client setuptools setuptools_scm wheel"
                // set devpi address, $DEV_PI is configured env variable in jenkins-slave-vmaas
                sh "devpi use ${DEV_PI} --set-cfg"
                // install iqe-tests
                sh "pip install --user --no-warn-script-location iqe-integration-tests iqe-clientv3-plugin iqe-current-ui-plugin"
                // install vulnerability plugin
                // sh "pip install --user --no-warn-script-location iqe-vulnerability-plugin"
                sh "pip install --user --no-warn-script-location -e vmaas_tests"
                sh "pip install --user --no-warn-script-location pytest-html"
                sh "pip install --user --no-warn-script-location pytest-report-parameters"
            }
        }

        stage("Deploy VMaaS") {
            // Deploy VMaaS to vmaas-qe project
            withStatusContext.custom("deploy") {
                stage("Login as deployer account") {
                    withCredentials([string(credentialsId: "openshift_token", variable: "TOKEN")]) {
                        sh "oc login https://${pipelineVars.devCluster} --token=${TOKEN}"
                    }
                    sh "oc project vmaas-qe"
                }

                checkOutRepo(targetDir: pipelineVars.e2eDeployDir, repoUrl: pipelineVars.e2eDeployRepoSsh, credentialsId: pipelineVars.gitSshCreds)
                sh "python3.6 -m venv ${pipelineVars.venvDir}"
                sh "${pipelineVars.venvDir}/bin/pip install --upgrade pip"
                dir(pipelineVars.e2eDeployDir) {
                    sh "${pipelineVars.venvDir}/bin/pip install -r requirements.txt"
                    // wipe old deployment
                    sh "${pipelineVars.venvDir}/bin/ocdeployer wipe -f vmaas-qe -l app=vmaas"
                    // git reference
                    String GIT_REF = "${env.BRANCH_NAME}"
                    if (env.BRANCH_NAME.startsWith("PR")) {
                        String GIT_PR = "${env.BRANCH_NAME}" - "PR-"
                        GIT_REF = "+refs/pull/${GIT_PR}/head"
                    }
                    // set needed env.yml
                    // build vmaas-webapp from Dockerfile-webapp-qe - it won't start app.py
                    sh """
                        # Create an env.yaml to have the builder pull from a different branch
                        echo "vmaas/vmaas-apidoc:" > builder-env.yml
                        echo "  parameters:" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                        echo "vmaas/vmaas-reposcan:" >> builder-env.yml
                        echo "  parameters:" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                        echo "vmaas/vmaas-webapp:" >> builder-env.yml
                        echo "  parameters:" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                        echo "    DOCKERFILE_PATH: Dockerfile-webapp-qe" >> builder-env.yml
                        echo "vmaas/vmaas-websocket:" >> builder-env.yml
                        echo "  parameters:" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                        echo "vmaas/vmaas-db:" >> builder-env.yml
                        echo "  parameters:" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                        echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml

                        # Deploy these customized builders into 'vmaas-qe' project
                        ${pipelineVars.venvDir}/bin/ocdeployer deploy -f --sets vmaas --template-dir buildfactory \
                            -e builder-env.yml vmaas-qe --secrets-local-dir secrets/sanitized
                    """
                    // deploy vmaas service set
                    sh "${pipelineVars.venvDir}/bin/ocdeployer deploy -f --sets vmaas \
                        --template-dir ../vmaas_tests/openshift/templates \
                        -e ../vmaas_tests/openshift/env/env.yml \
                        vmaas-qe --secrets-local-dir secrets/sanitized"
                }
            }
            
        }

        stage("Integration tests") {
            // Run integration tests
            withStatusContext.custom("integration-tests") {
                sh """
                    cd ~/.local/lib/python3.6/site-packages/iqe/conf
                    ln -rs ${WORKSPACE}/vmaas-yamls/conf/credentials.yaml
                """
                sh """
                    cd vmaas_tests/iqe_vulnerability/conf
                    ln -rs ${WORKSPACE}/vmaas-yamls/conf/settings.jenkins.yaml
                """
                stage("Run vmaas-webapp with coverage") {
                    // Start webapp as `coverage run ...` instead of `python ...` to collect coverage
                    sh '''
                        webapp_pod="$(oc get pods | grep 'Running' | grep 'webapp' | awk '{print $1}')"
                        oc exec "${webapp_pod}" -- bash -c "webapp/scl-enable.sh coverage run webapp/app.py --source webapp &>/proc/1/fd/1" &
                    '''
                }
                stage("Setup DB") {
                    withCredentials([string(credentialsId: "vmaas-bot-token", variable: "TOKEN")]) {
                    sh """
                        cd vmaas_tests
                        vmaas/scripts/setup_db.sh ${WORKSPACE}/vmaas-yamls/data/repolist.json \
                            http://vmaas-reposcan.vmaas-qe.svc:8081 \
                            http://vmaas-webapp.vmaas-qe.svc:8080 \
                            ${TOKEN}
                        sleep 10
                    """   
                    }
 
                }
                stage("Run tests") {
                    // Running pytest can result in six different exit codes:
                    // 0: All tests were collected and passed successfully
                    // 1: Tests were collected and run but some of the tests failed
                    // 2: Test execution was interrupted by the user
                    // 3: Internal error happened while executing tests
                    // 4: pytest command line usage error
                    // 5: No tests were collected
                    sh '''
                        cd vmaas_tests
                        pytest_status=0
                        # run only vmaas tests for now
                        if [ -d iqe_vulnerability/tests/vmaas ]; then
                            ~/.local/bin/iqe tests custom -v --junit-xml="iqe-junit-report.xml" --html="report.html" --self-contained-html iqe_vulnerability/tests/vmaas || pytest_status="$?"
                        else
                            ~/.local/bin/iqe tests plugin vulnerability -v --junit-xml="iqe-junit-report.xml" --html="report.html" --self-contained-html || pytest_status="$?"
                        fi
                        if [ "$pytest_status" -gt 1 ]; then
                            exit "$pytest_status"
                        fi
                        mkdir html_report
                        mv report.html html_report
                    '''
                }
            }
            junit "vmaas_tests/iqe-junit-report.xml"
        }

        stage("Code coverage") {
            // Notifies GitHub with the "continuous-integration/jenkins/coverage" status
            // Kill webapp and copy coverage in html format
            webapp_pod = sh(
                script: "oc get pods | grep 'Running' | grep 'webapp' | awk '{print \$1}'",
                returnStdout: true
            ).trim()

            sh "oc exec ${webapp_pod} -- pkill -sigint coverage"
            
            def status = 99
            status = sh(
                script: "oc exec ${webapp_pod} -- webapp/scl-enable.sh coverage html --fail-under=${codecovThreshold} --omit /usr/\\* -d /tmp/htmlcov",
                returnStatus: true
            )

            sh "mkdir htmlcov"
            sh "oc cp ${webapp_pod}:/tmp/htmlcov htmlcov"

            withStatusContext.coverage {
                assert status == 0
            }

            // run webapp's app.py again
            sh "oc exec ${webapp_pod} -- bash -c 'webapp/scl-enable.sh webapp/app.py &>/proc/1/fd/1' &"
        }

        stage("Publish in Polarion") {
            // Publish results for tagged commits in Polarion
            withCredentials([string(credentialsId: 'polarion_passwd', variable: 'PASSWORD'), 
                             string(credentialsId: 'polarion_user', variable: 'USER')]) {
                sh '''
                    last_commit="$(git rev-parse --short HEAD)"
                    versioned="$(git describe --tags --exact-match "$last_commit" 2>/dev/null)" || true
                    if [ -n "$versioned" ]; then
                        cd vmaas_tests
                        testrun_name="test-run-vmaas-$versioned"
                        ~/.local/bin/pip install dump2polarion
                        polarion_dumper.py -i iqe-junit-report.xml -t "$testrun_name" \
                            --user "$USER" --password "$PASSWORD" \
                            --log-level=debug --verify-timeout=1200 || true
                    fi
                '''
            }
        }

        stage("Publish HTML") {
            publishHTML (target: [
                  allowMissing: true,
                  alwaysLinkToLastBuild: true,
                  keepAll: true,
                  reportDir: 'htmlcov',
                  reportFiles: 'index.html',
                  reportName: "Coverage Report"
            ])
            publishHTML (target: [
                  allowMissing: true,
                  alwaysLinkToLastBuild: true,
                  keepAll: true,
                  reportDir: 'vmaas_tests/html_report',
                  reportFiles: 'report.html',
                  reportName: "Test Report"
            ])
        }
    }
}
