import json
import os
import requests
from common.dhis2_metadata_assessment.extract_assessment import download_integrity_checks
from common.evaluators.data_set_evaluator import evaluate_dataset
from common.evaluators.program_evaluator import evaluate_program
from common.metadata_exporter import download_support_metadata
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
    for i, program in enumerate(programs):
        print(f"Evaluating program {program['name']} (id: {program['id']}) [{i}/{len(programs)}])...")
        evaluate_program(program, server)




def evaluate_datasets(datasets: list, server: dict):

    for i, dataset in enumerate(datasets):
        print(f"Evaluating dataset {dataset['name']} (id: {dataset['id']}) [{i}/{len(datasets)}])...")
        evaluated = evaluate_dataset(dataset, server)
        


def execute():

    create_results_folders()

    server = json.load(open("config.json"))
    print(server)

    # download_support_metadata(server=server)
    # download_integrity_checks(server=server)

    # print("Fetching datasets...")
    # datasets = get_datasets(server)
    # print(f"Found {len(datasets)} datasets.")

    print("Fetching programs...")
    programs = get_programs(server)
    print(f"Found {len(programs)} programs.")

    # evaluate_datasets(datasets, server)
    evaluate_programs(programs, server)



if __name__ == "__main__":
    execute()