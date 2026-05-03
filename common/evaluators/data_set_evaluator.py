import json
from common.utils import get_headers, get_dataset_results_path
from common.metadata_exporter import export_dataset



def clean_dataset_export(dataset_export: dict):
    # Extract the main dataset id and name from the 'dataSets' key
    datasets = dataset_export.get("dataSets", [])
    main = datasets[0] if datasets else {}

    result = {
        "id": main.get("id"),
        "name": main.get("name"),
    }

    # For every other key that holds a list, keep only id and name per item
    for key, value in dataset_export.items():
        if key == "dataSets":
            continue
        if isinstance(value, list):
            result[key] = [
                {k: item[k] for k in ("id", "name") if k in item}
                for item in value
            ]

    return result


def evaluate_dataset(dataset: dict, server: dict):

    dataset_results_path = get_dataset_results_path()

    dataset_export = export_dataset(dataset['id'], server)
    cleaned_data_set =  clean_dataset_export(dataset_export)

    with open(f"{dataset_results_path}/{dataset['id']}.txt", "w") as f:
        json.dump(cleaned_data_set, f)




if __name__ == "__main__":
    pass