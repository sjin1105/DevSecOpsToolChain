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
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii1TYnB6THpzRnJMWTZGN3NZOHRsVjBMY1l4aFE0WWZOV3BLTnFMcDcxcTgifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tNXA1Z3EiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImYwZDgxN2MzLWZhNDUtNGVlNy1iMmU3LTg1YTM2NTliNWE5OCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.J8cDAoqSEO1hlLtf58AC-aV-w0CMQA9oxNFm1KZp5B-p6fGJqCluv6EiOVcZaGklzr4nbrvgzWJVItUv3MrougFnTIX_JT82LKHD2BHY9tyWKLgUrjot69QM07jEnBykmzAi87WoUqzYcA14xFFHI48HJDaanFTzgt-1d_kwT2Em74DYWQXNU-Pz-zuOW-Vct9zv8squOiyTeTpiN3q2-Np7TVnarJXaBxqVWV79y5Ou6RA_ku83P6bMWeUK1lSj2hkL-mdhD4uj9RA70LAt21Y8KMVL8KNgfNeZKLhNE4q3bTnm0-H549wXImnY6fFfWm4L-JlJABimty-hh6SVGQ"

def logging(request):
    return render(request, 'pybo/logging.html')


def monitor_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        
        # Kubernetes PODS 가져오기    
        request_url = "https://10.0.0.79:6443/api/v1/namespaces/monitor/pods/"# .format(request.POST['PN'])
        headers = {"Authorization": "Bearer {}".format(token)}
        api_response = requests.get(request_url, headers=headers, verify=False)
        api_json = api_response.json()
        pod_items = api_json['items']

        # Kubernetes SERVICES 가져오기
        request_url = "https://10.0.0.79:6443/api/v1/namespaces/{}/services/".format(request.POST['PN'])
        headers = {"Authorization": "Bearer {}".format(token)}
        api_response = requests.get(request_url, headers=headers, verify=False)
        api_json = api_response.json()
        service_items = api_json['items']
            
        context = {'project': project, 'pod_list' : pod_items, 'service_list' : service_items}
        return render(request, 'pybo/monitor.html', context)
    
def grafana(request):
    return render(request, 'pybo/grafana.html')