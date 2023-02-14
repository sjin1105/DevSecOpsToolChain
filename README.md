# DevSecOpsToolChain

Kubernetes Cluster와 Jenkins, SonarQube, Anchore, Dependency-Check를 위한 노드 1개

Docker image를 사용하여 Django 이미지 빌드
```
docker image build -t . 
```
Kubernetes에서 동작
Django Admin 페이지에서 필수 정보 입력

|   AS-IS                       |   TO-BE                           |
|:-----------------------------:|:---------------------------------:|
|프로젝트에 맞는 도구 검색        |각 단계에 맞는 도구 제공             |
|도구에 대한 이해도와 숙련도 요구  |최소한의 가이드라인으로 사용         |
|도구 각각의 대시보드 이동시간 소모|하나의 페이지에서 통합 관리          |
|프로젝트 진행시 보안 기능 미흡    |프로젝트를 진행하면서 보안 검사 진행  |

## 환경
- Ubuntu 20.04 focal
- OpenStack Zed

## 사용 도구
- Kubernetes = 1.22.9
- Docker
- PostgreSQL = 14.6
- Django = 4.1.5
- Longhorn = 1.4.0
- Jenkins = 2.375.2
- Argo CD = 2.5.4
- SonarQube = 8.9.10
- Dependency Check = 7.4.4
- Anchore = 0.9.4
- Harbor = 2.5.5


![구성도 drawio](https://user-images.githubusercontent.com/76959621/218671657-cdecc1a6-c49b-4250-8280-6fe6bc586f5f.png)

