
node {
  def app
  def dockerfile
  def anchorefile
  def repotag

  try {
    stage('Checkout') {
      // Clone the git repository
      checkout scm
      def path = sh returnStdout: true, script: "pwd"
      path = path.trim()
      dockerfile = path + "/Dockerfile"
      anchorefile = path + "/anchore_images"
    }

    stage('Build') {
      // Build the image and push it to a staging repository
      app = docker.build("test/test", "--network host -f Dockerfile .")
	    docker.withRegistry('https://192.168.160.244', 'harbor') {
	app.push("$BUILD_NUMBER")
	app.push("latest")
      }
      sh script: "echo Build completed"
    }

    stage('Parallel') {
      parallel Test: {
        app.inside {
            sh 'echo "Dummy - tests passed"'
        }
      },
      Analyze: {
        writeFile file: anchorefile, \
	      /*text: 'https://192.168.160.244'*/
	      text: "192.168.160.244" +  "/" + "test/test" + " " + dockerfile
        anchore name: anchorefile, \
	      engineurl: 'http://192.168.160.244:8228/v1', \
	      engineCredentialsId: 'admin', \
	      annotations: [[key: 'added-by', value: 'jenkins']], \
	      forceAnalyze: true
      }
    }
  } finally {
    stage('Cleanup') {
      // Delete the docker image and clean up any allotted resources
      sh script: "echo Clean up"
    }
  }
     stage('OWASP Dependency-Check Vulnerabilities ') {
        dependencyCheck additionalArguments: '''
		-s "." 
		-f "ALL"
		-o "./report/"
		--prettyPrint
		--disableYarnAudit''', odcInstallation: 'OWASP Dependency-check'
		dependencyCheckPublisher pattern: 'report/dependency-check-report.xml'
     }
     stage('SonarQube analysis') {
	    def scannerHome = tool 'sonarqube';
            withSonarQubeEnv('sonarserver'){
                    sh "${scannerHome}/bin/sonar-scanner \
		-Dsonar.projectKey=sonarqube \
		-Dsonar.host.url=http://192.168.160.244:9000 \
		-Dsonar.login=807e0f2bc82e3c377436e2b6292ed7bc73b04e24 \
		-Dsonar.sources=. \
		-Dsonar.report.export.path=sonar-report.json \
		-Dsonar.exclusions=report/* \
		-Dsonar.dependencyCheck.jsonReportPath=./report/dependency-check-report.json \
		-Dsonar.dependencyCheck.xmlReportPath=./report/dependency-check-report.xml \
		-Dsonar.dependencyCheck.htmlReportPath=./report/dependency-check-report.html"
         }
     }
        stage('SonarQube Quality Gate'){
    	 timeout(time: 1, unit: 'HOURS') {
              def qg = waitForQualityGate()
              if (qg.status != 'OK') {
                  error "Pipeline aborted due to quality gate failure: ${qg.status}"
              }
          
          }
     }
}
