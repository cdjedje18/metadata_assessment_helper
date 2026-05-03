import json
import os
import requests
from common.evaluators.data_set_evaluator import evaluate_dataset
from common.metadata_exporter import export_analysis_metadata
from common.utils import create_results_folders, get_headers, get_metadata_results_path


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



def evaluate_programs(programs: list, server: dict):
    for program in programs:
        url = f"{server['url']}/api/programs/{program['id']}/metadata.json"
        params = {"skipSharing": "true"}
        response = requests.get(url, headers=get_headers(server), params=params)
        response.raise_for_status()
        program_export = response.json()

    with open(f"results/program_{program['id']}.json", "w") as f:
        json.dump(program_export, f, indent=2)




def evaluate_datasets(datasets: list, server: dict):

    for i, dataset in enumerate(datasets):
        print(f"Evaluating dataset {dataset['name']} (id: {dataset['id']}) [{i}/{len(datasets)}])...")
        evaluated = evaluate_dataset(dataset, server)
        


def execute():

    create_results_folders()

    server = json.load(open("config.json"))
    print(server)

    export_analysis_metadata(server=server)

    # print("Fetching datasets...")
    # datasets = get_datasets(server)
    # print(f"Found {len(datasets)} datasets.")

    # # print("Fetching programs...")
    # # programs = get_programs(server)
    # # print(f"Found {len(programs)} programs.")

    # evaluate_datasets(datasets, server)
    # # evaluate_programs(programs, server)



if __name__ == "__main__":
    execute()