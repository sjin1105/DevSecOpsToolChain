from django.shortcuts import render, get_object_or_404
from ..models import Project, K8s, DNS
import requests
from django.http import JsonResponse
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def token_def():
    token = K8s.objects.values()[0]['TOKEN']
    return token
def grafana(request):
    print(DNS.objects.values())
    context = {'dns' : DNS.objects.values()[0]['domain']}
    return render(request, 'pybo/grafana.html', context)

def logging(request):
    context = {'dns' : DNS.objects.values()[0]['domain']}
    return render(request, 'pybo/logging.html', context)

def monitor(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {'project': project}
    return render(request, 'pybo/monitor.html', context)

def monitor_list(request):
    token = token_def()
    # Kubernetes PODS 가져오기    
    request_url = "https://10.0.0.79:6443/api/v1/namespaces/{}/pods/" .format(request.GET['PN'])
    headers = {"Authorization": "Bearer {}".format(token)}
    api_response = requests.get(request_url, headers=headers, verify=False)
    api_json = api_response.json()

    for item in range(len(api_json['items'])):
        api_json['items'][item]['metadata']['creationTimestamp'] = api_json['items'][item]['metadata']['creationTimestamp'].replace("T", " ")
        api_json['items'][item]['metadata']['creationTimestamp'] = api_json['items'][item]['metadata']['creationTimestamp'].replace("Z", "")

    pod_items = api_json['items']

    # Kubernetes SERVICES 가져오기
    request_url = "https://10.0.0.79:6443/api/v1/namespaces/{}/services/".format(request.GET['PN'])
    headers = {"Authorization": "Bearer {}".format(token)}
    api_response = requests.get(request_url, headers=headers, verify=False)
    api_json = api_response.json()

    for item in range(len(api_json['items'])):
        api_json['items'][item]['metadata']['creationTimestamp'] = api_json['items'][item]['metadata']['creationTimestamp'].replace("T", " ")
        api_json['items'][item]['metadata']['creationTimestamp'] = api_json['items'][item]['metadata']['creationTimestamp'].replace("Z", "")

    service_items = api_json['items']
 
    context = {'pod_list' : pod_items, 'service_list' : service_items}
    return JsonResponse(context)
    
