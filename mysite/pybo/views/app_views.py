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

project_name = "project"
argo_host = "http://argocd.xyz/"
request_url1 = """{}api/v1/session""".format(argo_host)
data1 = {'username':'admin','password':'python3.10'}
api_response = requests.post(request_url1, data=json.dumps(data1))
argocd_accesstoken = api_response.json()['token']

def app(request):
    return render(request, 'pybo/appcreate.html')

def webapp(request):
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
    flag = 0
    pj = Project.objects.values()
    for i in range(0, len(pj)):
        if pj[i]['id'] == int(request.POST['PID']):
            project = pj[i]
            flag = 1
            break
    if flag == 0:
        print("Project doesn't exist")
    
    if 'web' in request.POST:
        response = False
        helm_value0 = f"{request.POST['WNAME']}"
        helm_value1 = f"{request.POST['WPW']}"
        if request.POST['web'] == "tomcat":
            helm_repo = "https://charts.bitnami.com/bitnami"
            helm_version = "10.5.7"
        else:
            helm_repo = "https://charts.bitnami.com/bitnami"
            helm_version = "15.2.22"
        data = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": 
                { 
                    "name": "%s-%s" % (request.POST['PN'], request.POST['web']) 
                },
            "spec": {
                "destination": {
                    "name": "",
                    "namespace": f"{request.POST['PN']}",
                    "server": "https://kubernetes.default.svc"
                },
                "source": {
                    "path": "",
                    "repoURL": f"{helm_repo}",
                    "targetRevision": f"{helm_version}",
                    "chart" : f"{request.POST['web']}",
                    "helm" : { 
                        "parameters": [
                            { "name" : f"{request.POST['web']}" + "Username", "value" : f"{helm_value0}"},
                            { "name" : f"{request.POST['web']}" + "Password", "value" : f"{helm_value1}"},
                            { "name" : "service.type", "value" : "ClusterIP"},
                            { "name" : "ingress.enabled", "value" : "true"},
                            { "name" : "ingress.hostname", "value" : "%s%s.xyz" %(request.POST['PN'], request.POST['web'])},
                            { "name" : "ingress.annotations", "value" : 'kubernetes.io/ingress.class: "nginx"'},
                        ]
                    }
                },
                "project": f"{request.POST['PN']}",
                "syncPolicy": {
                    "automated": {},
                    "syncOptions": ["CreateNamespace=true", "ApplyOutOfSyncOnly=true"]
                }
            }
        }
        try:
            request_url = """{}api/v1/applications""".format(argo_host)
            headers = {"Authorization": "Bearer {}".format(argocd_accesstoken)}
            api_response = requests.post(request_url, data=json.dumps(data), headers=headers)
            context = {'project' : project, 'url' : "%s%s.xyz" %(request.POST['PN'], request.POST['web']), 'state' : ''}

            if api_response.ok:
                response = True
                print(f"argocd 애플리케이션 생성 성공: {project_name}")
            else:
                print("[332] create argocd application is failed: {}".format(api_response.json()))

        except Exception as e:
            print("[332] create argocd application is failed: {}".format(e))
        finally:
            return render(request, 'pybo/appcreate.html', context)
    else:
        context = {'project' : project, 'state' : 'None'}
    return render(request, 'pybo/appcreate.html', context)

    


def dbapp(request):
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
    flag = 0
    pj = Project.objects.values()
    for i in range(0, len(pj)):
        if pj[i]['id'] == int(request.POST['PID']):
            flag = 1
            project = pj[i]
            break
    if flag == 0:
        print("Project doesn't exist")

    if 'db' in request.POST:
        response = False
        helm_value0 = f"{request.POST['RPW']}"
        helm_value1 = f"{request.POST['UID']}"
        helm_value2 = f"{request.POST['UPW']}"
        helm_value3 = f"{request.POST['DB']}"
        if request.POST['db'] == "mariadb":
            helm_repo = "https://charts.bitnami.com/bitnami"
            helm_version = "11.4.2"
        else:
            helm_repo = "https://charts.bitnami.com/bitnami"
            helm_version = "9.4.6"
        data = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": 
                { 
                    "name": "%s-%s" % (request.POST['PN'], request.POST['db'])
                },
            "spec": {
                "destination": {
                    "name": "",
                    "namespace": f"{request.POST['PN']}",
                    "server": "https://kubernetes.default.svc"
                },
                "source": {
                    "path": "",
                    "repoURL": f"{helm_repo}",
                    "targetRevision": f"{helm_version}",
                    "chart" : f"{request.POST['db']}",
                    "helm": { 
                        "parameters": [
                            { "name" : "auth.rootPassword", "value" : f"{helm_value0}"},
                            { "name" : "auth.username", "value" : f"{helm_value1}"},
                            { "name" : "auth.password", "value" : f"{helm_value2}"},
                            { "name" : "auth.database", "value" : f"{helm_value3}"},
                            { "name" : "networkPolicy.enabled", "value" : "true" },
                            { "name" : "networkPolicy.allowExternal", "value" : "true" },
                        ]
                    }
                },
                "project": f"{request.POST['PN']}",
                "syncPolicy": {
                    "automated": {},
                    "syncOptions": ["CreateNamespace=true", "ApplyOutOfSyncOnly=true"]
                }
            }
        }
        try:
            request_url = """{}api/v1/applications""".format(argo_host)
            headers = {"Authorization": "Bearer {}".format(argocd_accesstoken)}
            api_response = requests.post(request_url, data=json.dumps(data), headers=headers)
            context = {'project' : project, 'url' : "%s%s.xyz" %(request.POST['PN'], request.POST['db']), 'state' : ''}

            if api_response.ok:
                response = True
                print(f"argocd 애플리케이션 생성 성공: {project_name}")
            else:
                print("[332] create argocd application is failed: {}".format(api_response.json()))

        except Exception as e:
            print("create argocd application is failed: {}".format(e))
        finally:
            return render(request, 'pybo/appcreate.html', context)
    else:
        context = {'project' : project, 'state' : 'None'}
    return render(request, 'pybo/appcreate.html', context)

    