import requests
from common.utils import get_headers
import os
import json
from common.utils import get_integrity_checks_path




def get_integrity_checks(server: dict):
    url = f"{server['url']}/api/dataIntegrity.json"
    params = {"paging": "false", "fields": "id,name"}
    response = requests.get(url, headers=get_headers(server), params=params)
    response.raise_for_status()
    return response.json()




def download_integrity_checks(server: dict):
    integrity_checks = get_integrity_checks(server)
    print(f"Downloaded {len(integrity_checks)} integrity checks.")

    for index, integrity_check in enumerate(integrity_checks):

        if os.path.exists(os.path.join(get_integrity_checks_path(), f"{integrity_check['name']}.txt")):
            print(f"Integrity check {integrity_check['name']} already exists, skipping download.")
            continue

        print(f"Downloading integrity check {index}/{len(integrity_checks)}: {integrity_check['name']}")

        url = f"{server['url']}/api/dataIntegrity/details?checks={integrity_check['name']}"
        response = requests.post(url, headers=get_headers(server))
        response.raise_for_status()

        if response.status_code == 200:
            url = f"{server['url']}/api/dataIntegrity/details?checks={integrity_check['name']}"
            response = requests.get(url, headers=get_headers(server))
            response.raise_for_status()
            check_details = response.json()

            output_path = os.path.join(get_integrity_checks_path(), f"{integrity_check['name']}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(check_details))




def execute():
    pass



if __name__ == "__main__":
    execute()