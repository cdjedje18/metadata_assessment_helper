


def get_headers(server:dict):
    return {
        "Authorization": f"Basic {server['auth']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }







if __name__ == "__main__":
    print("Hello, World!")