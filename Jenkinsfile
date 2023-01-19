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
     stage('K8S Manifest Update') {
         withCredentials([usernamePassword(credentialsId: 'git_key', passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {

			 sh('git config --global user.email "sjin110550@gmail.com"')
			 sh('git config --global user.name "sjin110550"')
			 sh('git checkout main')
			 sh('git pull https://github.com/seungjin-1105/ParkingReservationProject-kubernetes.git')
			 sh('sed -i "s|image: sjin1105/django.*|image: sjin1105/django:$BUILD_NUMBER|g" ./ArgoCD/django/django-deploy.yaml')
			 sh('git add .')
			 sh('git commit -m "$BUILD_NUMBER"')
			 sh('git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/seungjin-1105/ParkingReservationProject-kubernetes.git')
                    }
     }
}
