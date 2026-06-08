import requests

url = 'http://127.0.0.1:8000/copilot/query'
payload = {'user_query': 'Show hot leads'}
resp = requests.post(url, json=payload)
print(resp.status_code)
print(resp.text)
