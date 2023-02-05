from django.shortcuts import render, get_object_or_404, redirect
from models import Project, Jenkins, ArgoCD, K8s


argocd = ArgoCD.objects.all()
jks = Jenkins.objects.all()
k8s = K8s.objects.all()

print(argocd)