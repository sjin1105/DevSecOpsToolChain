from django import forms
from pybo.models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['NAME', 'KIND', 'GIT', 'GITTOKEN', 'SONARTOKEN']
        labels = {
            'NAME' : '이름',
            'KIND' : '종류',
            'GIT' : '주소',
            'GITTOKEN' : 'GIT 토큰',
            'SONARTOKEN' : 'SONAR 토큰'
        }
