node {
  def app
  def dockerfile
  def anchorefile
	
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
      app = docker.build("projects/$JOB_NAME", "--network host -f Dockerfile .")
	  docker.withRegistry('https://192.168.160.244', 'harbor') {
	    app.push("$BUILD_NUMBER")
	    app.push("latest")
      }
      sh script: "echo Build completed"
    }

    stage('Parallel Test') {
      parallel Test: {
        app.inside {
          sh 'echo "Dummy - tests passed"'
        }
      }
    }
	  
    /*stage('Anchore Image Scan') {
        writeFile file: anchorefile, text: "192.168.160.244/projects" + "/${JOB_NAME}" + ":${BUILD_NUMBER}" + " " + dockerfile
        anchore name: anchorefile, \
	      engineurl: 'http://192.168.160.244:8228/v1', \
	      engineCredentialsId: 'admin', \
	      annotations: [[key: 'added-by', value: 'jenkins']], \
	      forceAnalyze: true
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
    */  
    stage('SonarQube analysis') {
        def scannerHome = tool 'sonarqube';
        withSonarQubeEnv('sonarserver'){
            sh "${scannerHome}/bin/sonar-scanner \
	      -Dsonar.projectKey=sonarqube \
	      -Dsonar.host.url=http://192.168.160.244:9000 \
	      -Dsonar.login=807e0f2bc82e3c377436e2b6292ed7bc73b04e24 \
	      -Dsonar.sources=. \
	      -Dsonar.report.export.path=sonar-report.json \
	      -Dsonar.exclusions=*/** \
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
        }else{
	currentBuild.result = 'SUCCESS'
      	}
      }
    }
    /* stage ("Dynamic Analysis - DAST with OWASP ZAP") {
        sh "docker run -v ${pwd}:/zap/wrk/:rw --user root \
      -t owasp/zap2docker-stable zap-baseline.py \
	  -t http://192.168.160.233/ \
      -c gen.conf -J report_json -r report_html -d"
    } */ 	
  } catch (e) {
	echo "Exception=${e}"
        currentBuild.result = 'FAILURE'
	throw e
  } finally {
    stage('Cleanup') {
      // Delete the docker image and clean up any allotted resources
      sh script: "echo Clean up"
    	}	
     echo currentBuild.result
     if(currentBuild.result.equals("SUCCESS")){
	slackSend (channel: '#jenkins-notification', color: '#00FF00', message: "SUCESSFUL : '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }else{
	slackSend (channel: '#jenkins-notification', color: '#F01717', message: "${currentBuild.result} : Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }
   }
}
