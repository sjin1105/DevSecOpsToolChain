from django.shortcuts import render, get_object_or_404
from ..models import K8s, Project
import requests

def token_def():
    token = K8s.objects.values()[0]['TOKEN']
    return token

def domain_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        token = token_def()
        request_url = "https://10.0.0.79:6443/apis/networking.k8s.io/v1/namespaces/{}/ingresses/".format(request.POST['PN'])
        headers = {"Authorization": "Bearer {}".format(token), "Content-type": "application/yaml"}
        body ='''
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-%s-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: cert-manager-webhook-duckdns-production
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - %s.innogrid.duckdns.org
    secretName: %s.innogrid-tls-secret-production
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
    ''' %(request.POST['PN'], request.POST['PN'], request.POST['PN'], request.POST['PN'], request.POST['SN'], request.POST['SP'])

        api_response = requests.post(request_url, headers=headers, verify=False, data=(body))
        context = {'project' : project, "state" : 'create', 'domain' : '%s.innogrid.duckdns.org' %(request.POST['PN'])}
        return render(request, 'pybo/domain.html', context)
    else:
        context = {'project' : project, "state" : ''}
    return render(request, 'pybo/domain.html', context)

def domain_delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    token = token_def()
    request_url = "https://10.0.0.79:6443/apis/networking.k8s.io/v1/namespaces/{}/ingresses/".format(request.POST['PN'])
    headers = {"Authorization": "Bearer {}".format(token), "Content-type": "application/yaml"}

    api_response = requests.delete(request_url, headers=headers, verify=False)
    context = {'project' : project, 'state' : 'delete'}
    return render(request, 'pybo/domain.html', context)
