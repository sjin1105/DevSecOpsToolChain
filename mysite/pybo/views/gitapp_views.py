from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from ..models import Project
from django.utils import timezone
from django.http import HttpResponseNotAllowed
from ..forms import ProjectForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import pymysql
from time import sleep
import jenkins
import requests
import json
import base64

def docker(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {'project': project, 'state': ''}
    return render(request, 'pybo/docker.html', context)

def argocd(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {'project': project, 'state': ''}
    return render(request, 'pybo/yaml.html', context)

def create_jenkins(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']


    if request.method == "POST":

        # Jenkinsfile 생성
        jfile = """node {
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
		-Dsonar.projectKey=%s \
		-Dsonar.host.url=http://192.168.160.244:9000 \
		-Dsonar.login=%s \
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
        """ %(project.NAME, project.SONARTOKEN)  #project.NAME
        
        # 입력한 Data base64 변환
        base2 = jfile.encode(encoding='utf-8')
        ba64_2 = base64.b64encode(base2)
        result_data2 = ba64_2.decode('ascii')
        
        # 이미 존재하는 경우 sha값 가져오기
        request_url = "https://api.github.com/repos/{}/{}/contents/Jenkinsfile".format(userid, project.NAME)
        headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
        api_response = requests.get(request_url, headers=headers)
        api_json = api_response.json()
        try:
            sha = api_json['sha']
        except:
            sha = ""

        if sha == "":
            data2 = {
                "message": "from K8s project : {}".format(project.NAME),
                "content": "{}".format(result_data2),
            }
        else:
            data2 = {
                "message": "from K8s project : {}".format(project.NAME),
                "content": "{}".format(result_data2),
                "sha": "{}".format(sha),
            }
        
        # Jenkinsfile
        request_url2 = "https://api.github.com/repos/{}/{}/contents/Jenkinsfile".format(userid, project.NAME)
        headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
        api_response = requests.put(request_url2, data=json.dumps(data2), headers=headers)
        api_json = api_response.json()

        context = {'project': project, 'state': 'GitHub에 작성이 완료되었습니다.'}

        return render(request, 'pybo/github.html', context)


def github_listfile(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']

    if request.method == "POST":
        if request.POST['FN'] == 'back':
            addr = request.POST['PATH']
            if addr != '/':
                addr = addr[:-1]
            while addr[-1] != '/': 
                addr = addr[:-1]
            request_url = "https://api.github.com/repos/{}/{}/contents{}".format(userid, project.NAME, addr)
            headers = {"Accept": "application/vnd.github+json", "Authorization": "{}".format(project.GITTOKEN)}
            api_response = requests.get(request_url, headers=headers)
            api_json = api_response.json()
        else:
            # repo의 리스트 가져오기
            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
            headers = {"Accept": "application/vnd.github+json", "Authorization": "{}".format(project.GITTOKEN)}
            api_response = requests.get(request_url, headers=headers)
            api_json = api_response.json()
            addr = request.POST['PATH'] + request.POST['FN'] + '/'
            
        context = {'project': project, 'addr' : addr, 'git_list' : api_json, 'state' : ''}
        return render(request, 'pybo/gitlist.html', context)
    else:
        request_url = "https://api.github.com/repos/{}/{}/contents/".format(userid, project.NAME)
        api_response = requests.get(request_url, headers=headers)
        api_json = api_response.json()
        context = {'project': project, 'addr' : '/', 'git_list' : api_json, 'state' : ''}
        return render(request, 'pybo/gitlist.html', context)

# github file 수정 or 생성
def github_createfile(request, project_id):

    project = get_object_or_404(Project, pk=project_id)
    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']
    
    if request.method == "GET":
        # 이미 존재하는 경우 sha값 가져오기
        request_url = "https://api.github.com/repos/{}/{}/contents/{}{}".format(userid, project.NAME, request.GET['PATH'], request.GET['FN'])
        
        headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
        api_response = requests.get(request_url, headers=headers)
        api_json = api_response.json()
        try:
            sha = api_json['sha']
        except:
            sha = ""

        if sha == "":
            data = {
                "message": "from K8s project : {}".format(project.NAME),
                "content": "",
            }
            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.GET['PATH'], request.GET['FN'])
            headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
            api_response = requests.put(request_url, data=json.dumps(data), headers=headers)
            api_json = api_response.json()
            data = ""
        
        
        else:
            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.GET['PATH'], request.GET['FN'])
            headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
            api_response = requests.get(request_url, headers=headers)
            api_json = api_response.json()
            api_byte = base64.b64decode(api_json['content'])
            data = api_byte.decode('ascii')
        
        context = {'file' : request.GET['FN'], 'path' : request.GET['PATH'], 'content' : data, 'project' : project, 'state' : ''}

        return render(request, 'pybo/gitfile_modify.html', context)
        

# 파일 수정하여 업로드
def github_editfile(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']

    if request.method == "POST":
        
        # 이미 존재하는 경우 sha값 가져오기
        request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
        headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
        api_response = requests.get(request_url, headers=headers)
        api_json = api_response.json()
        try:
            sha = api_json['sha']
        except:
            sha = ""
        
        if sha == "":
            context = {'project': project, 'state': '잘못되었습니다.'}
        else:
            data = request.POST['data']
            print(data)
            base = data.encode(encoding='utf-8')
            ba64 = base64.b64encode(base)
            result_data = ba64.decode('ascii')

            data = {
                "message": "from K8s project : {}".format(project.NAME),
                "content": "{}".format(result_data),
                "sha": "{}".format(sha),
            }

            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
            headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
            api_response = requests.put(request_url, data=json.dumps(data), headers=headers)
            api_json = api_response.json()

        context = {'project': project, 'state': 'Git Hub에 작성이 완료되었습니다.', 'path': request.POST['PATH']}

        return render(request, 'pybo/github.html', context)


# 파일 삭제
def github_deletefile(request, project_id):

    project = get_object_or_404(Project, pk=project_id)

    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']

    if request.method == "POST":
        
        # 이미 존재하는 경우 sha값 가져오기
        request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
        headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
        api_response = requests.get(request_url, headers=headers)
        api_json = api_response.json()
        try:
            sha = api_json['sha']
        except:
            sha = ""
        
        if sha == "":
            context = {'project': project, 'state': '잘못되었습니다.'}
        else:
            data = {
                "message": "from K8s project : {}".format(project.NAME),
                "sha": "{}".format(sha),
            }

            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
            headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
            api_response = requests.delete(request_url, data=json.dumps(data), headers=headers)
            api_json = api_response.json()

        context = {'project': project, 'state': 'File 삭제가 완료되었습니다.', 'path': request.POST['PATH']}

        return render(request, 'pybo/github.html', context)
