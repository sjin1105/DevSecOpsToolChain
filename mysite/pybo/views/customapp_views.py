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

host = "http://192.168.160.244:8080"
username = "admin" #jenkins username here
password = "admin" # Jenkins user password / api token here
server = jenkins.Jenkins(host, username=username, password=password)

project_name = "project"
argo_host = "http://argocd.xyz/"
request_url1 = """{}api/v1/session""".format(argo_host)
data1 = {'username':'admin','password':'python3.10'}
api_response = requests.post(request_url1, data=json.dumps(data1))
argocd_accesstoken = api_response.json()['token']

def jenkins_api(request):
    addr = request.POST['addr']
    pj = Project.objects.values()
    flag = 0
    for i in range(0, len(pj)):
        if pj[i]['id'] == int(request.POST['PID']):
            project = pj[i]
            flag = 1
            break
    if flag == 0:
        print("Project doesn't exist")
    
    myConfig = server.get_job_config(request.POST['PN'])
    # github 주소가 등록되어 있지 않으면
    if "<url>https://github.com/</url>" in myConfig:
        new = myConfig.replace('<url>https://github.com/</url>', '<url>%s</url>' %(addr))
        server.reconfig_job(request.POST['PN'], new)
        server.build_job(request.POST['PN'])
        context = {'state' : '빌드 완료', 'project' : project}
        
    # 해당 github 주소가 이미 등록되어 있는 상태면   
    elif "<url>{}</url>".format(addr) in myConfig: 
        server.build_job(request.POST['PN'])
        context = {'state' : '빌드 완료', 'project' : project}
        
    # 다른 github 주소가 이미 등록되어 있는 상태면    
    else:
        context = {'state' : '이미 Github 레포지토리가 등록되어 있습니다. 다른 레포지토리를 사용하시려면 프로젝트를 새로 생성히세요.', 'project' : project}    

    if request.POST['KIND'] == 'GitHub App':
        return render(request, 'pybo/github.html', context)
    else:
        return render(request, 'pybo/custom.html', context)

def jenkins_backup(request):
    init = open('./init_conf', 'r')
    f = init.read()
    server.reconfig_job('test', f)
    init.close()
    return redirect('pybo:index')

def customapp(request):
    """, project_name, app_name, parameter0, parameter1, parameter2, parameter3
        argocd application 생성
        파라미터:
            argocd_host: argocd 주소
            argocd_access_token: argocd 액세스 토큰
            argocd_project_name: 배포할 argocd 프로젝트 이름
            app_name: 배포할 앱 이름
            deploy_kubernetes_namespace: 배포할 쿠버네티스 namespace
            app_git_remoterepo: argocd가 배포할 앱 git 주소
        리턴:
            True: 생성성공
            False: 생성실패
    """

    pj = Project.objects.values()

    flag = 0
    for i in range(0, len(pj)):
        if pj[i]['id'] == int(request.POST['PID']):
            project = pj[i]
            flag = 1
            break
    if flag == 0:
        print("Project doesn't exist")

    response = False
    GitURL = f"{request.POST['ADDR']}"
    GitFolder = f"{request.POST['GIT']}"
    data = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": 
            { 
                "name": f"{request.POST['PN']}" 
            },
        "spec": {
            "destination": {
                "name": "",
                "namespace": f"{request.POST['PN']}",
                "server": "https://kubernetes.default.svc"
            },
            "source": {
                "path": f"{GitFolder}",
                "repoURL": f"{GitURL}",
                "targetRevision": "main",
                "directory": {
                    "recurse": True,
                },
            },
            "project": f"{request.POST['PN']}",
            "syncPolicy": {
                "automated": {},
                "syncOptions": ["CreateNamespace=true", "ApplyOutOfSyncOnly=true"]
            }
        }
    }
    context = {'project' : project, 'state' : '배포 완료'}
    try:
        request_url = """{}api/v1/applications""".format(argo_host)
        headers = {"Authorization": "Bearer {}".format(argocd_accesstoken)}
        api_response = requests.post(request_url, data=json.dumps(data), headers=headers)

        if api_response.ok:
            response = True
            print(f"argocd 애플리케이션 생성 성공: {project_name}")
        else:
            print("[332] create argocd application is failed: {}".format(api_response.json()))

    except Exception as e:
        print("[332] create argocd application is failed: {}".format(e))
    finally:
        return render(request, 'pybo/custom.html', context)