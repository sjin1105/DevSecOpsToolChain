from django.shortcuts import render, get_object_or_404, redirect
from ..models import Project

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