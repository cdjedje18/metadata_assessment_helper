import os


def get_headers(server:dict):
    return {
        "Authorization": f"Basic {server['auth']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def get_dataset_results_path():
    return f"results/datasets"

def get_program_results_path():
    return f"results/programs"


def create_results_folders():
    os.makedirs(get_dataset_results_path(), exist_ok=True)
    os.makedirs(get_program_results_path(), exist_ok=True)







if __name__ == "__main__":
    print("Hello, World!")