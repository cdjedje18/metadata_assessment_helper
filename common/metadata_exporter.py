import json
import requests
from common.utils import get_headers


def export_dataset(dataset: str, server: dict):
    url = f"{server['url']}/api/dataSets/{dataset}/metadata.json"
    params = {"skipSharing": "true"}
    response = requests.get(url, headers=get_headers(server), params=params)
    response.raise_for_status()
    return response.json()


def export_program(program: str, server: dict):
    url = f"{server['url']}/api/programs/{program}/metadata.json"
    params = {"skipSharing": "true"}
    response = requests.get(url, headers=get_headers(server), params=params)
    response.raise_for_status()
    return response.json()



if __name__ == "__main__":
    print("Hello, World!")