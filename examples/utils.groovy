// JenkinsDoc - Example Groovy Utility Functions
// ==============================================
// Use this file to test Go-To-Definition feature
//
// INSTRUCTIONS:
// 1. Keep this file in the same folder as test-Jenkinsfile
// 2. In test-Jenkinsfile, load this library and call these functions
// 3. HOVER over function names in Jenkinsfile
// 4. Use go-to-definition (if supported by your Sublime setup)

/**
 * Deploy application to production environment
 *
 * This function handles the deployment process including:
 * - Building the application
 * - Running tests
 * - Deploying to production servers
 *
 * @param version The version to deploy
 * @return boolean Success status
 */
def deployToProduction(String version = '1.0.0') {
    echo "Deploying version ${version} to production..."

    // Build
    sh 'mvn clean package'

    // Deploy
    sh "deploy.sh ${version}"

    echo "Deployment complete!"
    return true
}

/**
 * Deploy application to staging environment
 *
 * @param branch The git branch to deploy
 */
def deployToStaging(String branch = 'develop') {
    echo "Deploying ${branch} to staging..."

    git branch: branch, url: 'https://github.com/example/repo.git'

    sh 'mvn clean package'
    sh 'deploy-staging.sh'

    echo "Staging deployment complete!"
}

/**
 * Send notification via email or Slack
 *
 * @param message The notification message
 * @param channel Optional notification channel
 */
def sendNotification(String message, String channel = 'general') {
    echo "Sending notification to ${channel}: ${message}"

    // Example: Send Slack notification
    // slackSend(
    //     channel: channel,
    //     message: message,
    //     color: 'good'
    // )

    // Example: Send email
    // mail(
    //     to: 'team@example.com',
    //     subject: 'Jenkins Build Notification',
    //     body: message
    // )
}

/**
 * Run tests with configurable options
 *
 * @param testType Type of tests to run (unit, integration, e2e)
 * @param parallel Whether to run tests in parallel
 */
def runTests(String testType = 'unit', boolean parallel = false) {
    echo "Running ${testType} tests..."

    switch(testType) {
        case 'unit':
            sh 'mvn test'
            break

        case 'integration':
            sh 'mvn verify -Pintegration-tests'
            break

        case 'e2e':
            sh 'npm run test:e2e'
            break

        default:
            error("Unknown test type: ${testType}")
    }

    echo "${testType} tests complete!"
}

/**
 * Build Docker image
 *
 * @param imageName Name of the Docker image
 * @param tag Image tag (default: latest)
 * @return String Full image name with tag
 */
def buildDockerImage(String imageName, String tag = 'latest') {
    echo "Building Docker image: ${imageName}:${tag}"

    sh """
        docker build -t ${imageName}:${tag} .
        docker tag ${imageName}:${tag} ${imageName}:${env.BUILD_NUMBER}
    """

    return "${imageName}:${tag}"
}

/**
 * Push Docker image to registry
 *
 * @param imageName Full image name with tag
 * @param registry Docker registry URL
 */
def pushDockerImage(String imageName, String registry = 'docker.io') {
    echo "Pushing ${imageName} to ${registry}"

    withCredentials([usernamePassword(
        credentialsId: 'docker-credentials',
        usernameVariable: 'DOCKER_USER',
        passwordVariable: 'DOCKER_PASS'
    )]) {
        sh """
            echo \$DOCKER_PASS | docker login ${registry} -u \$DOCKER_USER --password-stdin
            docker push ${imageName}
        """
    }

    echo "Push complete!"
}

/**
 * Clean up old artifacts
 *
 * @param daysToKeep Number of days to keep artifacts
 */
def cleanupArtifacts(int daysToKeep = 7) {
    echo "Cleaning up artifacts older than ${daysToKeep} days..."

    sh """
        find ./target -name "*.jar" -mtime +${daysToKeep} -delete
        find ./dist -name "*.zip" -mtime +${daysToKeep} -delete
    """

    echo "Cleanup complete!"
}

/**
 * Get current Git commit information
 *
 * @return Map containing commit hash, author, and message
 */
def getGitInfo() {
    def commitHash = sh(
        script: 'git rev-parse HEAD',
        returnStdout: true
    ).trim()

    def commitAuthor = sh(
        script: 'git log -1 --pretty=format:%an',
        returnStdout: true
    ).trim()

    def commitMessage = sh(
        script: 'git log -1 --pretty=format:%s',
        returnStdout: true
    ).trim()

    return [
        hash: commitHash,
        author: commitAuthor,
        message: commitMessage
    ]
}

/**
 * Check if service is healthy
 *
 * @param url Service health check URL
 * @param maxRetries Maximum number of retries
 * @return boolean Health status
 */
def checkServiceHealth(String url, int maxRetries = 5) {
    echo "Checking service health at ${url}..."

    def retry = 0
    def healthy = false

    while (retry < maxRetries && !healthy) {
        try {
            def response = sh(
                script: "curl -f -s -o /dev/null -w '%{http_code}' ${url}",
                returnStdout: true
            ).trim()

            if (response == '200') {
                healthy = true
                echo "Service is healthy!"
            } else {
                echo "Health check returned ${response}, retrying..."
                sleep(10)
            }
        } catch (Exception e) {
            echo "Health check failed: ${e.message}"
            sleep(10)
        }

        retry++
    }

    return healthy
}

/**
 * Create release tag
 *
 * @param version Version number for the tag
 * @param message Tag message
 */
def createReleaseTag(String version, String message = '') {
    echo "Creating release tag: v${version}"

    def tagMessage = message ?: "Release version ${version}"

    sh """
        git tag -a v${version} -m '${tagMessage}'
        git push origin v${version}
    """

    echo "Release tag created!"
}

/**
 * Rollback deployment
 *
 * @param environment Target environment
 * @param previousVersion Version to rollback to
 */
def rollback(String environment, String previousVersion) {
    echo "Rolling back ${environment} to version ${previousVersion}..."

    sh "rollback.sh ${environment} ${previousVersion}"

    // Verify rollback
    if (checkServiceHealth("https://${environment}.example.com/health")) {
        echo "Rollback successful!"
    } else {
        error("Rollback failed - service unhealthy!")
    }
}

// TEST USAGE IN JENKINSFILE:
// ---------------------------
/*
@Library('jenkins-shared-library') _

pipeline {
    agent any

    stages {
        stage('Deploy') {
            steps {
                script {
                    // HOVER over 'deployToProduction' below
                    // Should show function documentation
                    utils.deployToProduction('1.2.3')

                    // HOVER over 'sendNotification'
                    utils.sendNotification('Deployment complete!')

                    // HOVER over 'getGitInfo'
                    def gitInfo = utils.getGitInfo()
                    echo "Commit: ${gitInfo.hash}"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // HOVER over 'runTests'
                    utils.runTests('integration', true)
                }
            }
        }

        stage('Docker') {
            steps {
                script {
                    // HOVER over 'buildDockerImage'
                    def image = utils.buildDockerImage('myapp', '1.0.0')

                    // HOVER over 'pushDockerImage'
                    utils.pushDockerImage(image)
                }
            }
        }
    }

    post {
        always {
            script {
                // HOVER over 'cleanupArtifacts'
                utils.cleanupArtifacts(30)
            }
        }
    }
}
*/

// Return this to make functions available
return this
