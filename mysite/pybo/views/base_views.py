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


def index(request):
    project = Project.objects.all()
    context = {'project': project, 'state' : ''}
    return render(request, 'pybo/mainpage.html', context) 

def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {'project': project, 'state' : ''}
    if project.KIND == 'App':
        return render(request, 'pybo/appcreate.html', context)
    elif project.KIND == 'Custom App':
        return render(request, 'pybo/custom.html', context)
    elif project.KIND == 'GitHub App':
        return render(request, 'pybo/github.html', context)
    else:
        context = {'project': project, 'state' : '오류'}
        return render(request, 'pybo/mainpage.html', context)