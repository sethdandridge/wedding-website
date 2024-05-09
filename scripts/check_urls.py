import requests

with open("instance/urls.txt") as f:
    urls = [f.split("\t")[2].strip() for f in f.readlines()[1:]]

for url in urls:
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"URL {url} returned status code {response.status_code}")
    else:
        print(f"URL {url} is working")
