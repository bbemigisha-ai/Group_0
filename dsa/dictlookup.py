import json
from pathlib import Path
import time

JSON_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "converted_transactions"
    / "transactions.json"
)


def load_transactions():
    if JSON_FILE.exists():
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []


def build_transaction_lookup(transaction_list):
    transaction_lookup = {}

    for transaction in transaction_list:
        transaction_data = transaction.get("Transactions", {})
        tx_id = transaction_data.get("txId")

        if tx_id is not None:
            transaction_lookup[tx_id] = transaction

    return transaction_lookup


def dict_lookup(transaction_lookup, transaction_id):
    return transaction_lookup.get(transaction_id)


if __name__ == "__main__":
    transaction_list = load_transactions()
    transaction_lookup = build_transaction_lookup(transaction_list)

    # Get the first 20 transaction IDs
    transaction_ids = []

    for transaction in transaction_list[:25]:
        transaction_data = transaction.get("Transactions", {})
        tx_id = transaction_data.get("txId")

        if tx_id is not None:
            transaction_ids.append(tx_id)

    start_time = time.perf_counter()

    for transaction_id in transaction_ids:
        dict_lookup(transaction_lookup, transaction_id)

    end_time = time.perf_counter()

    total_time = end_time - start_time

    print("Dictionary Lookup")
    print(f"Records searched: {len(transaction_ids)}")
    print(f"Total execution time: {total_time:.8f} seconds")

    if transaction_ids:
        average_time = total_time / len(transaction_ids)
        print(f"Average search time: {average_time:.8f} seconds")