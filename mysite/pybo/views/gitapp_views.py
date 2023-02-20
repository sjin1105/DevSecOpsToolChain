from django.shortcuts import render, get_object_or_404, redirect
from ..models import Project, K8s
import requests
import json
import base64

def token_def():
    token = K8s.objects.values()[0]['TOKEN']
    return token

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
        jfile = ''' 
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
    stage('OWASP Dependency-Check Vulnerabilities ') {
    dependencyCheck additionalArguments: """
	    -s "." 
	    -f "ALL"
	    -o "./report/"
	    --prettyPrint
	    --disableYarnAudit""", odcInstallation: 'OWASP-Dependency-check'
	    dependencyCheckPublisher pattern: 'report/dependency-check-report.xml'
  }
    stage('SonarQube analysis') {
        def scannerHome = tool 'sonarqube';
        withSonarQubeEnv('sonarserver'){
            sh "${scannerHome}/bin/sonar-scanner \
	      -Dsonar.projectKey=%s \
	      -Dsonar.host.url=http://192.168.160.229:9000 \
	      -Dsonar.login=%s \
	      -Dsonar.sources=. \
	      -Dsonar.report.export.path=sonar-report.json \
	      -Dsonar.exclusions=report/* \
	      -Dsonar.dependencyCheck.jsonReportPath=./report/dependency-check-report.json \
	      -Dsonar.dependencyCheck.xmlReportPath=./report/dependency-check-report.xml \
	      -Dsonar.dependencyCheck.htmlReportPath=./report/dependency-check-report.html"
        }
    }
    stage('Build') {
      // Build the image and push it to a staging repository
      app = docker.build("innogrid/$JOB_NAME", "--network host -f Dockerfile .")
      	
	docker.withRegistry('https://core.innogrid.duckdns.org', 'harbor') {
	app.push("$BUILD_NUMBER")
	app.push("latest")
	
      }
      sh script: "echo Build completed"
    }
    stage('Grype Image Scan') {
    	docker.withRegistry('https://core.innogrid.duckdns.org', 'harbor') {
	    sh 'grype innogrid/$JOB_NAME:latest --scope AllLayers'
	}
      }
      currentBuild.result = "SUCCESS"
  } catch (e) {
	echo "Exception=${e}"
        currentBuild.result = 'FAILURE'
	throw e
  } finally {
    stage('Cleanup') {
      sh script: "echo Clean up"
    	}	
     echo currentBuild.result
     // send slack notification
     if(currentBuild.result.equals("SUCCESS")){
	slackSend (channel: '#jenkins-notification', color: '#00FF00', message: "build success : Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }else{
	slackSend (channel: '#jenkins-notification', color: '#F01717', message: "build failed : Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")
     }
   }
}
        ''' %(project.NAME, project.SONARTOKEN)  #project.NAME
        
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

        return redirect('pybo:github_listfile', project_id=project.id)


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
    
    if request.method == "POST":
        # 이미 존재하는 경우 sha값 가져오기
        request_url = "https://api.github.com/repos/{}/{}/contents/{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
        
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
            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
            headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
            api_response = requests.put(request_url, data=json.dumps(data), headers=headers)
            api_json = api_response.json()
            data = ""
            filekind = 'file'
            extension = ''
        
        else:
            request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], request.POST['FN'])
            headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
            api_response = requests.get(request_url, headers=headers)
            api_json = api_response.json()
            api_byte = base64.b64decode(api_json['content'])
            try:
                data = api_byte.decode('ascii')
                filekind = 'file'
                extension = ''
            except:
                if '.' in api_json['name']:
                    data = api_json['content']
                    blank = request.POST['FN'].split('.')
                    extension = blank[len(blank) - 1]
                    filekind = 'image'
                else:
                    data = ''
                    filekind = ''
                    extension = ''
        
        context = {'file' : request.POST['FN'], 'path' : request.POST['PATH'], 'content' : data, 'filekind' : filekind, 'ext' : extension, 'project' : project, 'state' : ''}

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

        # context = {'project': project, 'state': 'Git Hub에 작성이 완료되었습니다.', 'path': request.POST['PATH'], 'addr' : request.POST['PATH']}

        return redirect('pybo:github_listfile', project_id=project.id)


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

        # context = {'project': project, 'state': 'File 삭제가 완료되었습니다.', 'path': request.POST['PATH']}

        return redirect('pybo:github_listfile', project_id=project.id)

def github_fileupload(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # github userid 가져오기
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(project.GITTOKEN)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    userid = api_json['login']

    data = request.FILES['file'].read()
    name = request.FILES['file'].name

    ba64 = base64.b64encode(data)
    result_data = ba64.decode('ascii')

    # 이미 존재하는 경우 sha값 가져오기
    request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], name)
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
            "content": "{}".format(result_data),
        }
    else:
        data = {
            "message": "from K8s project : {}".format(project.NAME),
            "content": "{}".format(result_data),
            "sha": "{}".format(sha),
        }
    
    # Jenkinsfile
    request_url = "https://api.github.com/repos/{}/{}/contents{}{}".format(userid, project.NAME, request.POST['PATH'], name)
    headers = {"Authorization": "Bearer {}".format(project.GITTOKEN), "Accept": "application/vnd.github+json"}
    api_response = requests.put(request_url, data=json.dumps(data), headers=headers)
    api_json = api_response.json()

    return redirect('pybo:github_listfile', project_id=project.id)
