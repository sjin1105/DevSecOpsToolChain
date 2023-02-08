from django.contrib import admin
from .models import Project, Jenkins, ArgoCD, K8s, DNS

# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['NAME']

class JenkinsAdmin(admin.ModelAdmin):
    search_fields = ['HOST']

class ArgoCDAdmin(admin.ModelAdmin):
    search_fields = ['HOST']

class K8sAdmin(admin.ModelAdmin):
    search_fields = ['NAME']

class DNSAdmin(admin.ModelAdmin):
    search_fields = ['NAME']

admin.site.register(Project, ProjectAdmin)
admin.site.register(Jenkins, JenkinsAdmin)
admin.site.register(ArgoCD, ArgoCDAdmin)
admin.site.register(K8s, K8sAdmin)
admin.site.register(DNS, DNSAdmin)

