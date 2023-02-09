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
	  docker.withRegistry('https://core.innogrid.duckdns.org', 'harbor') {
	    app.push("$BUILD_NUMBER")
	    app.push("latest")
      }
      sh script: "echo Build completed"
    }
  }
}
