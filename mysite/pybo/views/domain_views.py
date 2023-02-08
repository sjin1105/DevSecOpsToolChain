from django.shortcuts import render, get_object_or_404
from ..models import K8s, Project
import requests

def token_def():
    token = K8s.objects.values()[0]['TOKEN']
    return token

def domain_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    token = token_def()
    request_url = "https://10.0.0.79:6443/apis/networking.k8s.io/v1/namespaces/{}/ingresses/".format(request.POST['PN'])
    headers = {"Authorization": "Bearer {}".format(token), "Content-type": "application/yaml"}

    body ='''
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
    name: nginx-django-ingress
    annotations:
        kubernetes.io/ingress.class: "nginx"
        nginx.ingress.kubernetes.io/rewrite-target: /
        nginx.ingress.kubernetes.io/ssl-redirect: "false"
    spec:
    rules:
    - host: %s.innogrid.duckdns.org
        http:
        paths:
        - path: /
            pathType: Prefix
            backend:
            service:
                name: %s
                port:
                number: %s
    ''' %(request.POST['PN'], request.POST['SN'], request.POST['SP'])

    api_response = requests.post(request_url, headers=headers, verify=False, data=(body))
    context = {'project' : project, "state" : '', 'domain' : '%s.innogrid.duckdns.org' %(request.POST['PN'])}
    if project.KIND == 'Custom App':
        return render(request, 'pybo/custom.html', context)
    else:
        return render(request, 'pybo/github.html', context)
