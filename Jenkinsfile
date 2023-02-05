 node {
  def app
  def dockerfile
  def anchorefile
	
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
      app = docker.build("sjin1105/inno", "--network host -f Dockerfile .")
	  docker.withRegistry('https://registry.hub.docker.com', 'docker') {
	    app.push("$BUILD_NUMBER")
	    app.push("latest")
      }
      sh script: "echo Build completed"
    }
}
