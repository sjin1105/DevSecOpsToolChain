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
    path('jenkins_api/<int:project_id>', customapp_views.jenkins_api, name='jenkins_api'),
    path('jenkins_build_info/<int:project_id>', customapp_views.jenkins_build_info, name='jenkins_build_info'),
    path('jenkins_build_info/', customapp_views.jenkins_build_info, name='jenkins_build_info'),
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
    path('github_list/upload/<int:project_id>', gitapp_views.github_fileupload, name='github_fileupload'),

    # monitor_views.py
    path('monitor/', monitor_views.monitor_list, name='monitor_list'),
    path('monitor/<int:project_id>', monitor_views.monitor, name='monitor'),
    path('logging/', monitor_views.logging, name='logging'),
    path('grafana/', monitor_views.grafana, name='grafana'),
]
