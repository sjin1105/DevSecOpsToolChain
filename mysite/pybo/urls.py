from django.urls import path
from .views import app_views, base_views, customapp_views, gitapp_views, project_views, monitor_views

app_name = 'pybo'

urlpatterns = [
    # base_views.py
    path('', base_views.index, name='index'),
    path('<int:project_id>/', base_views.detail, name='detail'),
    
    # project_views.py
    path('project/', project_views.project, name='project'),
    path('project/delete/<int:project_id>/', project_views.project_delete, name='project_delete'),
    
    # app_views.py
    path('app/', app_views.app, name='app'),
    path('webapp/', app_views.webapp, name='webapp'),
    path('dbapp/', app_views.dbapp, name='dbapp'),

    # custom_views.py
    path('jenkins_api/', customapp_views.jenkins_api, name='jenkins_api'),
    path('jenkins_backup/', customapp_views.jenkins_backup, name='jenkins_backup'),
    path('customapp/', customapp_views.customapp, name='customapp'),

    # gitapp_views.py
    path('docker/<int:project_id>/', gitapp_views.docker, name='docker'),
    path('docker/create/<int:project_id>', gitapp_views.create_jenkins, name='create_jenkins'),
    path('YAML/<int:project_id>/', gitapp_views.argocd, name='argocd'),
    path('github_list/<int:project_id>/', gitapp_views.github_listfile, name='github_listfile'),
    path('github_list/create/<int:project_id>', gitapp_views.github_createfile, name='github_createfile'),
    path('github_list/edit/<int:project_id>', gitapp_views.github_editfile, name='github_editfile'),
    path('github_list/delete/<int:project_id>', gitapp_views.github_deletefile, name='github_deletefile'),

    # monitor_views.py
    path('monitor/<int:project_id>', monitor_views.monitor_list, name='monitor_list'),
    path('logging/', monitor_views.logging, name='logging'),
    path('grafana/', monitor_views.grafana, name='grafana'),
]
