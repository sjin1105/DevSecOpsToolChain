from unittest.util import _MAX_LENGTH
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import requests
import string
import re
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii1TYnB6THpzRnJMWTZGN3NZOHRsVjBMY1l4aFE0WWZOV3BLTnFMcDcxcTgifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tNXA1Z3EiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImYwZDgxN2MzLWZhNDUtNGVlNy1iMmU3LTg1YTM2NTliNWE5OCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.J8cDAoqSEO1hlLtf58AC-aV-w0CMQA9oxNFm1KZp5B-p6fGJqCluv6EiOVcZaGklzr4nbrvgzWJVItUv3MrougFnTIX_JT82LKHD2BHY9tyWKLgUrjot69QM07jEnBykmzAi87WoUqzYcA14xFFHI48HJDaanFTzgt-1d_kwT2Em74DYWQXNU-Pz-zuOW-Vct9zv8squOiyTeTpiN3q2-Np7TVnarJXaBxqVWV79y5Ou6RA_ku83P6bMWeUK1lSj2hkL-mdhD4uj9RA70LAt21Y8KMVL8KNgfNeZKLhNE4q3bTnm0-H549wXImnY6fFfWm4L-JlJABimty-hh6SVGQ"
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create your models here.

def name_validate(value):
    for char in value:
        if char in string.punctuation:
            raise ValidationError("특수문자는 사용할수 없습니다.")
    request_url = "https://10.0.0.79:6443/api/v1/namespaces/"
    headers = {"Authorization": "Bearer {}".format(token)}
    api_response = requests.get(request_url, headers=headers, verify=False)
    api_json = api_response.json()
    service_items = api_json['items']
    name_list = []
    for item in service_items:
        name_list.append(item['metadata']['name'])
    if value in name_list:
        raise ValidationError("중복되는 이름이 있습니다.")
    else:
        reg = re.compile('^[a-zA-Z][0-9a-zA-Z]*')
        if not reg.match(value):
            raise ValidationError("문자로 시작해야 합니다.")
        return value

def git_validate(value):
    try:
        api_response = requests.post(value)
    except:
        raise ValidationError("URL 형식이 아닙니다.")
    reg = re.compile('^(https):\/\/github\.com\/[0-9a-zA-Z]*\/[-_\.0-9a-zA-Z]*\.(git)$')
    if not reg.match(value):
        raise ValidationError("Git Repo 주소가 아닙니다.")
    if api_response.status_code != 200:
        raise ValidationError("유효한 Git Repo가 아닙니다.")
    else:
        return value

def gittoken_validate(value):
    message = ''
    request_url = "https://api.github.com/user"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer {}".format(value)}
    api_response = requests.get(request_url, headers=headers)
    api_json = api_response.json()
    print(message)
    try:
        message = api_json['message']
    except:
        return value
    raise ValidationError("Token이 잘못되었습니다.")

class Project(models.Model):
    NAME = models.CharField(max_length=50, null=False, validators=[name_validate])
    KIND = models.CharField(max_length=50, null=False)
    GIT = models.URLField(max_length=200,  blank=True, validators=[git_validate])
    GITTOKEN = models.CharField(max_length=100,  blank=True, validators=[gittoken_validate])
    SONARTOKEN = models.CharField(max_length=100,  blank=True)
    PASSWORD = models.CharField(max_length=100, null=False)

class Jenkins(models.Model):
    HOST = models.CharField(max_length=100, null=False)
    USER = models.CharField(max_length=50, null=False)
    PASSWORD = models.CharField(max_length=50, null=False)

class ArgoCD(models.Model):
    HOST = models.CharField(max_length=100, null=False)
    USER = models.CharField(max_length=50, null=False)
    PASSWORD = models.CharField(max_length=50, null=False)
    
class K8s(models.Model):
    TOKEN = models.CharField(max_length=1200, null=False)

class DNS(models.Model):
    domain = models.CharField(max_length=200, null=False)

