import requests

request_url = "http://192.168.160.244:9000/api/issues/search"
user = ("admin", "admin123")
params = {
    'componentKeys': "helloworld",
}
api_response = requests.get(request_url, params=params, auth=user)
api_json = api_response.json()
print(api_json)
api_json = api_json['issues']

for issue in api_json:
    print(issue['rule'])
    print(issue['component'])
    print(issue['project'])
    print(issue['message'])
    print(issue['severity'])
    print('\n')

