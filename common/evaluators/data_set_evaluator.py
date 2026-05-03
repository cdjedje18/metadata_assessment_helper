import json
import os
import re
from common.utils import get_dataset_results_path, get_metadata_results_path
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




def get_dependency_metadata(dataset:dict):
    metadata_path = get_metadata_results_path()
    data_element_ids = {item.get("id") for item in dataset.get("dataElements", []) if item.get("id")}
    dataset_indicator_ids = {item.get("id") for item in dataset.get("indicators", []) if item.get("id")}

    def read_collection(file_name: str, key: str):
        file_path = os.path.join(metadata_path, file_name)
        if not os.path.exists(file_path):
            return []

        with open(file_path, "r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)

        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get(key, [])
        return []

    def object_mentions_uids(obj: dict, uids: set):
        if not uids:
            return False
        serialized = json.dumps(obj)
        for uid in uids:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(uid)}(?![A-Za-z0-9])", serialized):
                return True
        return False

    def compact(items: list):
        compacted = []
        seen = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            compacted.append({"id": item_id, "name": item.get("name")})
        return compacted

    indicators = read_collection("indicators.txt", "indicators")
    dependent_indicators = []
    for indicator in indicators:
        indicator_id = indicator.get("id") if isinstance(indicator, dict) else None
        if not indicator_id or indicator_id in dataset_indicator_ids:
            continue
        if object_mentions_uids(indicator, data_element_ids):
            dependent_indicators.append(indicator)

    # dependent_indicators.extend(dataset.get("indicators", []))
    dependency_uids = data_element_ids.union({item.get("id") for item in dependent_indicators if item.get("id")})
    dependency_uids = dependency_uids.union(dataset_indicator_ids)

    visualization_files = {
        "visualizations": ("visualizations.txt", "visualizations"),
        "eventVisualizations": ("eventVisualizations.txt", "eventVisualizations"),
        "maps": ("maps.txt", "maps"),
        "eventCharts": ("eventCharts.txt", "eventCharts"),
        "eventReports": ("eventReports.txt", "eventReports"),
    }

    analysis_matches = {}
    for key, (file_name, collection_key) in visualization_files.items():
        collection = read_collection(file_name, collection_key)
        analysis_matches[key] = [item for item in collection if isinstance(item, dict) and object_mentions_uids(item, dependency_uids)]

    visualization_ids = {
        item.get("id")
        for item in analysis_matches.get("visualizations", [])
        if isinstance(item, dict) and item.get("id")
    }

    dashboards = read_collection("dashboards.txt", "dashboards")
    dependent_dashboards = [
        dashboard
        for dashboard in dashboards
        if isinstance(dashboard, dict) and object_mentions_uids(dashboard, visualization_ids)
    ]

    dependecy_metadata = {
        "id": dataset.get("id"),
        "name": dataset.get("name"),
        "otherIndicators": compact(dependent_indicators),
        "visualizations": compact(analysis_matches.get("visualizations", [])),
        "eventVisualizations": compact(analysis_matches.get("eventVisualizations", [])),
        "maps": compact(analysis_matches.get("maps", [])),
        "eventCharts": compact(analysis_matches.get("eventCharts", [])),
        "eventReports": compact(analysis_matches.get("eventReports", [])),
        "dashboards": compact(dependent_dashboards),
    }

    new_dataset = {**dataset}
    for key, items in dependecy_metadata.items():
        if key not in ("id", "name"):
            new_dataset[key] = items
    
    return new_dataset






def evaluate_dataset(dataset: dict, server: dict):

    dataset_results_path = get_dataset_results_path()

    dataset_export = export_dataset(dataset['id'], server)
    cleaned_data_set =  clean_dataset_export(dataset_export)
    dependency_metadata = get_dependency_metadata(cleaned_data_set)

    with open(f"{dataset_results_path}/{dataset['id']}.txt", "w") as f:
        json.dump(dependency_metadata, f)




if __name__ == "__main__":
    pass