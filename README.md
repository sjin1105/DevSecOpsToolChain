# DevSecOpsToolChain

Kubernetes Cluster와 Jenkins, SonarQube, Anchore, Dependency-Check를 위한 노드 1개

Docker image를 사용하여 Django 이미지 빌드
```
docker image build -t . 
```
Kubernetes에서 동작
Django Admin 페이지에서 필수 정보 입력

|AS-IS|TO-BE|
|:---:|:---:|
|- 프로젝트에 맞는 도구 검색| - 각 단계에 맞는 도구 제공|

![구성도 drawio](https://user-images.githubusercontent.com/76959621/218671657-cdecc1a6-c49b-4250-8280-6fe6bc586f5f.png)

