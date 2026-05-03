import json
import os
import re
from common.utils import get_program_results_path, get_metadata_results_path
from common.metadata_exporter import export_program



def clean_program_export(program_export: dict):
    programs = program_export.get("programs", [])
    main = programs[0] if programs else {}

    result = {
        "id": main.get("id"),
        "name": main.get("name"),
        "programType": main.get("programType"),
    }

    # For every other key that holds a list, keep only id and name per item
    for key, value in program_export.items():
        if key == "programs":
            continue
        if isinstance(value, list):
            result[key] = [
                {k: item[k] for k in ("id", "name") if k in item}
                for item in value
            ]

    return result




def get_dependency_metadata(program: dict):
    metadata_path = get_metadata_results_path()
    data_element_ids = {item.get("id") for item in program.get("dataElements", []) if item.get("id")}
    program_indicator_ids = {item.get("id") for item in program.get("programIndicators", []) if item.get("id")}

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

    # Other program indicators that reference this program's data elements
    all_program_indicators = read_collection("programIndicators.txt", "programIndicators")
    dependent_program_indicators = []
    for indicator in all_program_indicators:
        indicator_id = indicator.get("id") if isinstance(indicator, dict) else None
        if not indicator_id or indicator_id in program_indicator_ids:
            continue
        if object_mentions_uids(indicator, data_element_ids):
            dependent_program_indicators.append(indicator)

    # Regular indicators referencing this program's data elements or program indicators
    all_indicators = read_collection("indicators.txt", "indicators")
    dependent_indicators = [
        ind for ind in all_indicators
        if isinstance(ind, dict)
        and ind.get("id") not in program_indicator_ids
        and object_mentions_uids(ind, data_element_ids.union(program_indicator_ids))
    ]

    dependency_uids = (
        data_element_ids
        .union(program_indicator_ids)
        .union({item.get("id") for item in dependent_program_indicators if item.get("id")})
        .union({item.get("id") for item in dependent_indicators if item.get("id")})
    )

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
        analysis_matches[key] = [
            item for item in collection
            if isinstance(item, dict) and object_mentions_uids(item, dependency_uids)
        ]

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

    dependency_metadata = {
        "id": program.get("id"),
        "name": program.get("name"),
        "otherProgramIndicators": compact(dependent_program_indicators),
        "otherIndicators": compact(dependent_indicators),
        "visualizations": compact(analysis_matches.get("visualizations", [])),
        "eventVisualizations": compact(analysis_matches.get("eventVisualizations", [])),
        "maps": compact(analysis_matches.get("maps", [])),
        "eventCharts": compact(analysis_matches.get("eventCharts", [])),
        "eventReports": compact(analysis_matches.get("eventReports", [])),
        "dashboards": compact(dependent_dashboards),
    }

    new_program = {**program}
    for key, items in dependency_metadata.items():
        if key not in ("id", "name"):
            new_program[key] = items

    return new_program




def evaluate_program(program: dict, server: dict):

    program_results_path = get_program_results_path()

    program_export = export_program(program['id'], server)
    cleaned_program = clean_program_export(program_export)
    # dependency_metadata = get_dependency_metadata(cleaned_program)

    with open(f"{program_results_path}/{program['id']}.txt", "w") as f:
        json.dump(cleaned_program, f)




if __name__ == "__main__":
    pass
