/*
 * Pipeline for running integration tests in Jenkins job with 
 * every pull request or change in master
 *
 * Requires: https://github.com/RedHatInsights/insights-pipeline-lib
 */

@Library("github.com/RedHatInsights/insights-pipeline-lib@v3") _

// Code coverage failure threshold
codecovThreshold = 89

pipelineUtils.cancelPriorBuilds()
runStages()

def deployVmaas(project) {
    gitUtils.withStatusContext("deploy") {
        dir(pipelineVars.e2eDeployDir) {
            String GIT_REF = "${env.BRANCH_NAME}"
            if (env.BRANCH_NAME.startsWith("PR")) {
                String GIT_PR = "${env.BRANCH_NAME}" - "PR-"
                GIT_REF = "+refs/pull/${GIT_PR}/head"
            }
            // set needed env.yml
            // build vmaas-webapp from Dockerfile-webapp-qe - it won't start main.py
            sh """
                # Create an env.yaml to have the builder pull from a different branch
                echo "vmaas/vmaas-reposcan:" >> builder-env.yml
                echo "  parameters:" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                echo "vmaas/vmaas-webapp:" >> builder-env.yml
                echo "  parameters:" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                echo "    DOCKERFILE_PATH: webapp/Dockerfile-qe" >> builder-env.yml
                echo "vmaas/vmaas-websocket:" >> builder-env.yml
                echo "  parameters:" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml
                echo "vmaas/vmaas-db:" >> builder-env.yml
                echo "  parameters:" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_REF: ${GIT_REF}" >> builder-env.yml
                echo "    SOURCE_REPOSITORY_URL: ${scmVars.GIT_URL}" >> builder-env.yml

                # Deploy these customized builders into 'vmaas-qe' project
                ocdeployer deploy -f --sets vmaas --template-dir buildfactory \
                    -e builder-env.yml ${project} --secrets-local-dir secrets/sanitized
            """
            // deploy vmaas service set
            sh "ocdeployer deploy -f --sets vmaas \
                --template-dir ../vulnerability/openshift/templates \
                -e ../vulnerability/openshift/env/env.yml \
                ${project} --secrets-local-dir secrets/sanitized"
        }
    }
}

def runStages() {
    // withNode is a helper to spin up a jnlp slave using the Kubernetes plugin, and run the body code on that slave
    openShiftUtils.withNode() {
        lock("vmaas-qe-deploy") {
            stage("Check out repos") {
                // check out source again to get it in this node"s workspace
                scmVars = checkout scm
                gitUtils.checkOutRepo(targetDir: pipelineVars.e2eDeployDir, repoUrl: pipelineVars.e2eDeployRepoSsh, credentialsId: pipelineVars.gitSshCreds)
                // checkout vmaas_tests git repository
                gitUtils.checkOutRepo(targetDir: "vulnerability", repoUrl: "https://github.com/RedHatInsights/vmaas_tests", credentialsId: "github")
            }

            stage("Login to oc cluster") {
                withCredentials([string(credentialsId: "openshift_token", variable: "TOKEN")]) {
                    sh "oc login https://${pipelineVars.devCluster} --token=${TOKEN}"
                }
                sh "oc project vmaas-qe"
            }

            stage("Pip install") {
                String pip_check
                try {
                    sh "pip install -U iqe-integration-tests pytest-html"
                    sh "iqe plugin install vulnerability"

                    dir(pipelineVars.e2eDeployDir) {
                        sh "pip install -r requirements.txt"
                    }

                    pip_check = sh(
                        script: "pip check || true",
                        returnStdout: true
                    ).trim()
                    if (pip_check.contains("has requirement attrs>=19.2.0")) {
                        // workaround for incorrect pinned version in iqe-tests
                        sh "pip install attrs>=19.2.0"
                    }
                } catch (err) {
                    echo("Error during installing test dependencies!")
                    echo(err.toString())
                    throw err
                }
            }

            stage("Inject local settings") {
                withCredentials([file(credentialsId: "vmaas-settings-local-yaml", variable: "settings")]) {
                    sh "cp \$settings \$IQE_VENV/lib/python3.6/site-packages/iqe_vulnerability/conf"
                }
            }

            stage("Wipe test environment") {
                sh "ocdeployer wipe -f vmaas-qe -l app=vmaas"
                // make sure that DB volume is deleted
                sh "oc delete pvc vmaas-db-data || true"
            }

            stage("Deploy VMaaS") {
                // Deploy VMaaS to vmaas-qe project
                try {
                    deployVmaas("vmaas-qe")
                } catch (err) {
                    echo("Error during VMaaS deploy! Look at oc logs in Artifacts.")
                    echo(err.toString())
                    openShiftUtils.collectLogs(project: "vmaas-qe")
                    throw err
                }
            }

            stage("Integration tests") {
                // Run integration tests
                gitUtils.withStatusContext("integration-tests") {
                    stage("Run vmaas-webapp with coverage") {
                        // Start webapp as `coverage run ...` instead of `python ...` to collect coverage
                        sh '''
                            webapp_pod="$(oc get pods | grep 'Running' | grep 'webapp' | awk '{print $1}')"
                            oc exec "${webapp_pod}" -- bash -c "coverage run main.py --source webapp &>/proc/1/fd/1" &
                        '''
                    }
                    stage("Setup DB") {
                        withCredentials([string(credentialsId: "vmaas-bot-token", variable: "TOKEN"),
                                        file(credentialsId: "repolist-json", variable: "REPOLIST")]) {
                            sh """
                                cd vulnerability
                                vmaas/scripts/setup_db.sh ${REPOLIST} \
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
                        String LONG_RUNNING = ""
                        if (env.BRANCH_NAME == "master") {
                            LONG_RUNNING = "--long-running"
                        }
                        pytest_status = sh(
                            script: "iqe tests plugin vulnerability -vvv -r s -k vmaas/ ${LONG_RUNNING} --html='report.html' --self-contained-html --generate-report",
                            returnStatus: true
                        )
                        assert pytest_status <= 1 : "Pytest error: ${pytest_status}"

                        sh '''
                            mkdir html_report
                            mv report.html html_report
                        '''
                    }
                }
                openShiftUtils.collectLogs(project: "vmaas-qe")
                junit "iqe-junit-report.xml"
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
                    script: "oc exec ${webapp_pod} -- coverage html --fail-under=${codecovThreshold} --omit /opt/\\* -d /tmp/htmlcov",
                    returnStatus: true
                )

                sh "mkdir htmlcov"
                sh "oc cp ${webapp_pod}:/tmp/htmlcov htmlcov"

                gitUtils.withStatusContext("coverage") {
                    assert status == 0
                }

                // run webapp's main.py again
                sh "oc exec ${webapp_pod} -- bash -c 'main.py &>/proc/1/fd/1' &"
            }

            stage("Publish in Polarion") {
                // Publish results for tagged commits in Polarion
                sh '''
                    last_commit="$(git rev-parse --short HEAD)"
                    versioned="$(git describe --tags --exact-match "$last_commit" 2>/dev/null)" || true
                    if [ -n "$versioned" ]; then
                        iqe results plugin vulnerability -t test-run-vmaas-$versioned
                    fi
                '''
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
                    reportDir: 'html_report',
                    reportFiles: 'report.html',
                    reportName: "Test Report"
                ])
            }
        }
    }
}
