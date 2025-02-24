import requests

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get("https://www.google.com/search?q=국내맥주시장+news&tbm=nws", headers=headers)
print(response.text)