import json
import os
import requests
from common.utils import get_headers, get_metadata_results_path




def download_support_metadata():
    server = json.load(open("config.json"))
    

    dashboards_uids = requests.get(f"{server['url']}/api/sqlViews/nvFGz1u31S0/data.json?paging=false", headers=get_headers(server))
    dashboards_uids.raise_for_status()
    dashboards_uids = dashboards_uids.json().get('listGrid').get("rows", [])
    print(f"Found {len(dashboards_uids)} dashboard UIDs.")

    # print(dashboards_uids)

    dashboards = []
    for uid in sorted(dashboards_uids):
        url = f"{server['url']}/api/dashboards/{uid[0]}.json"
        print(f"Downloading dashboard with UID {uid[0]}...")
        response = requests.get(url, headers=get_headers(server))
        response.raise_for_status()
        dashboards.append(response.json())

    output_path = os.path.join(get_metadata_results_path(), "dashboards.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboards, f)

    return dashboards


def export_analysis_metadata(server: dict):

    # download_support_metadata()

    endpoints = {
        "visualizations": "visualizations",
        "eventVisualizations": "eventVisualizations",
        "maps": "maps",
        "eventCharts": "eventCharts",
        "eventReports": "eventReports"
    }

    metadata = {}
    for key, endpoint in endpoints.items():
        print(f"Downloading {key} metadata...")
        url = f"{server['url']}/api/{endpoint}.json"
        params = {"paging": "false"}
        response = requests.get(url, headers=get_headers(server), params=params)
        response.raise_for_status()
        print(f"Downloaded {key} metadata with {len(response.json().get(endpoint, []))} items.")
        
        output_dir = get_metadata_results_path()
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{key}.txt")
        with open(output_file, "w", encoding="utf-8") as file_handle:
            file_handle.write(response.text)







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