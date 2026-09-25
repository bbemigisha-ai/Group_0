import xml.etree.ElementTree as ET
import re
import json

INPUT_FILE = "modified_sms_v2.xml"
OUTPUT_FILE = "transactions.json"

# starting of with the main core helper function to extract the number and amount from the body
def extract_number(body, pattern, default=None):
    match = re.search(pattern, body)
    if match:
        return int(match.group(1).replace(',', ''))
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

    sender = extract_name(body, "from") if txn_type == "incoming_money" else None
    recipient = extract_name(body, "to") if txn_type in ["transfer", "payment", "airtime_purchase", "bundle_purchase"] else None

    # this is the record style dictionary that will hold all the extracted information from the sms
    record = {
        "id": new_id,
        "type": txn_type,
        "amount": extract_amount(body),
        "fee": extract_fee(body),
        "balance": extract_balance(body),
        "sender": sender,
        "recipient": recipient,
        "timestamp": sms_element.get("readable_date", ""),
        "raw_body": body,

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