import xml.etree.ElementTree as ET
import re
import json

INPUT_FILE = "data/raw/modified_sms_v2.xml"
OUTPUT_FILE = "data/converted_transactions/transactions.json"

# this dictionary will hold the mapping of customer names to their unique IDs
CUSTOMER_LOOKUP = {}
_customer_id_counter = 1


# this function assigns a given customerID for a given name
def get_or_create_customer_id(name):
    global _customer_id_counter
    if not name:
        return None
    if name not in CUSTOMER_LOOKUP:
        CUSTOMER_LOOKUP[name] = _customer_id_counter
        _customer_id_counter += 1
    return CUSTOMER_LOOKUP[name]


# starting of with the main core helper function to extract the number and amount from the body
def extract_number(body, pattern, default=None):
    match = re.search(pattern, body)
    if match:
        return int(match.group(1).replace(",", ""))
    return default


# now we extract the amount, fee and balance from the body of the sms using regex patterns
def extract_amount(body):
    return extract_number(body, r"([\d,]+)\s*RWF")


def extract_fee(body):
    return extract_number(body, r"Fee was:?\s*([\d,]+)\s*RWF", default=0)


def extract_balance(body):
    return extract_number(body, r"Balance:?\s*([\d,]+)\s*RWF", default=None)


# now extracting the name of the sender or recepient from the body of the sms using regex patterns
def extract_name(body, keyword):
    pattern = keyword + r"\s+([A-Za-z][A-Za-z .]*?)\s*(?:\(|\d|has|from|$)"
    match = re.search(pattern, body)
    if match:
        return match.group(1).strip()
    return None


# now we classify the type of transaction based on the content of the sms body
def classify(body):
    text = body.lower()
    if "received" in text:
        return "incoming_money"
    if "bank deposit" in text:
        return "deposit"
    if "transferred to" in text:
        return "transfer"
    if "airtime" in text:
        return "airtime_purchase"
    if "bundle" in text or "data bundle" in text:
        return "bundle_purchase"
    if "payment of" in text:
        return "payment"
    return "other"


# parsing the sms and extracting the relevant information to create a structured record
def parse_sms(sms_element, new_id):
    body = sms_element.get("body", "")
    txn_type = classify(body)

    # now we extract the name based on the transaction type
    sender = extract_name(body, "from") if txn_type == "incoming_money" else None
    recipient = (
        extract_name(body, "to")
        if txn_type in ["transfer", "payment", "airtime_purchase", "bundle_purchase"]
        else None
    )

    if txn_type == "incoming_money":
        active_customer_name = sender
        active_role = "sender"
    else:
        active_customer_name = recipient
        active_role = "recepient"

    sender_id = get_or_create_customer_id(sender)
    recipient_id = get_or_create_customer_id(recipient)
    active_customer_id = get_or_create_customer_id(active_customer_name)

    # this is the record style dictionary that will hold all the extracted information from the sms
    record = {
        "txCategories": {
            "categoryID": f"CAT_{txn_type.upper()}",
            "categoryName": txn_type,
            "description": f"Transaction category for {txn_type}",
        },
        "customers": {
            "customerID": active_customer_id,
            "customerName": active_customer_name,
            "phoneNumber": sms_element.get("address", ""),
        },
        "Transactions": {
            "txId": new_id,
            "categoryID": f"CAT_{txn_type.upper()}",
            "recipientID": recipient_id,
            "senderID": sender_id,
            "txDate": sms_element.get("readable_date", ""),
            "txTime": sms_element.get("readable_time", ""),
            "updatedBalance": extract_balance(body),
            "txAmount": extract_amount(body),
            "txFee": extract_fee(body),
            "currency": "RWF",
            "status": "SUCCESS",
        },
        "SystemLogs": {
            "logID": new_id,
            "txID": new_id,
            "createdAt": sms_element.get("readable_date", ""),
            "rawMessage": body,
        },
        "CustomerTransaction": {
            "customerTxID": new_id,
            "customerID": active_customer_id,
            "txID": new_id,
            "role": active_role,
        },
    }
    return record


# the main function to parse the XML file and save the extracted transactions to a JSON file
def main():
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()

    transactions = []
    for i, sms in enumerate(root.findall("sms"), start=1):
        transactions.append(parse_sms(sms, i))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

    print(f"Parsed {len(transactions)} transactions and saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
