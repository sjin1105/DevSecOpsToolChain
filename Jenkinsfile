node {
     stage('Clone repository') {
	 checkout scm
     }
     stage('Build image') {
         app = docker.build("sjin1105/django", "--network host .")
     }
     stage('Push image') {
         docker.withRegistry('https://registry.hub.docker.com', 'docker') {
         app.push("$BUILD_NUMBER")
	 app.push("latest")
         }
     }
}
