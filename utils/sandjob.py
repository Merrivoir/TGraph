import os

accounts = {
    "turqel": {
        "id": 5994311190,
        "api": os.getenv("TFIVE"),
        "hash": os.getenv("TSIX")
    },
    "merrivoir": {
        "id": 1912365148,
        "api": os.getenv("TONE"),
        "hash": os.getenv("TTWO")
    },
    "fisker": {
        "id": 6710310438,
        "api": os.getenv("TTHREE"),
        "hash": os.getenv("TFOUR")
    }
}

keys = list(accounts.keys())
n = 1

for account in accounts:
    print(f"{n} - {account}")
    n = n + 1

choose = int(input("Выберите аккаунт: ")) - 1

api = accounts[keys[choose]]["api"]
hash = accounts[keys[choose]]["hash"]
id = accounts[keys[choose]]["id"]