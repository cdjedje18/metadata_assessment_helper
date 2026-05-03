import json
import requests
from common.utils import get_headers


def get_datasets(server: dict):
    url = f"{server['url']}/api/dataSets.json"
    params = {"fields": "id,name", "paging": "false"}
    response = requests.get(url, headers=get_headers(server), params=params)
    response.raise_for_status()
    return response.json().get("dataSets", [])


def get_programs(server: dict):
    url = f"{server['url']}/api/programs.json"
    params = {"fields": "id,name,programType", "paging": "false"}
    response = requests.get(url, headers=get_headers(server), params=params)
    response.raise_for_status()
    return response.json().get("programs", [])



def execute():
    
    config = json.load(open("config.json"))
    print(config)

    print("Fetching datasets...")
    datasets = get_datasets(config)
    print(f"Found {len(datasets)} datasets.")

    print("Fetching programs...")
    programs = get_programs(config)
    print(f"Found {len(programs)} programs.")


if __name__ == "__main__":
    execute()