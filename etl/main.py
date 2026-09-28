import base64
import binascii
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path

SOURCE_JSON_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "converted_transactions"
    / "transactions.json"
)

API_JSON_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "converted_transactions"
    / "api_transactions.json"
)

USERS = {"Karyna": "kk89", "Bertha": "bm67", "Nadiv": "ng25", "Guest": "getout"}

# validation scheme for PUT and/or POST data
REQUIRED_FIELDS = [
    "categoryID",
    "recipientID",
    "senderID",
    "txDate",
    "txTime",
    "updatedBalance",
    "txAmount",
    "txFee",
    "currency",
]

NUMBER_Fields = {
    "recipientID": int,
    "senderID": int,
    "updatedBalance": float,
    "txAmount": float,
    "txFee": float,
}


def validate_transaction(data):

    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if field not in data or data[field] in ("", None)
    ]
    if missing_fields:
        return None, f"Missing fields: {', '.join(missing_fields)}"

    # to not accidentally modify original dict while validation happens

    cleaned_data = data.copy()

    for field, converter in NUMBER_Fields.items():
        try:
            cleaned_data[field] = converter(data[field])
        except (ValueError, TypeError):
            return None, f"Field '{field}' must be a valid number"

    # Obviously, transactions have to be > 0

    if cleaned_data["txAmount"] <= 0:
        return None, "txAmount must be greater than zero"

    # to check that transaction fee is not -ve

    if cleaned_data["txFee"] < 0:
        return None, "txFee CANNOT be in the negative"

    return cleaned_data, None


def check_auth(header):
    if not header:
        return False

    try:
        scheme, encoded = header.split(" ", 1)

        if scheme != "Basic" or not encoded:
            return False

        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")

        username, password = decoded.split(":", 1)

    except (ValueError, UnicodeDecodeError, binascii.Error):
        return False
    return USERS.get(username) == password


def load_transactions():
    file_path = API_JSON_FILE if API_JSON_FILE.exists() else SOURCE_JSON_FILE

    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if file_path == API_JSON_FILE:
        return records

    return [record["Transactions"] for record in records if "Transactions" in record]


def save_transactions(records):
    with API_JSON_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)


class MomoTxHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def require_auth(self):
        auth_header = self.headers.get("Authorization", None)

        if not check_auth(auth_header):
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.send_header(
                "WWW-Authenticate", 'Basic realm="Access to /transactions"'
            )
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Invalid username or password"}).encode()
            )
            return False
        return True

    def do_GET(self):
        if not self.require_auth():
            return

        records = load_transactions()

        if self.path == "/transactions":
            self._set_headers(200)
            self.wfile.write(json.dumps(records).encode("utf-8"))
            return

        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]
            transaction = next(
                (record for record in records if str(record["txId"]) == transaction_id),
                None,
            )
            if transaction is None:
                self._set_headers(404)
                self.wfile.write(
                    json.dumps({"error": "Transaction couldn't be found"}).encode(
                        "utf-8"
                    )
                )
                return
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps(transaction).encode("utf-8"))
                return
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))

    def do_POST(self):
        if not self.require_auth():
            return

        records = load_transactions()

        if self.path == "/transactions":
            content_type = self.headers.get("Content-Type")

            if content_type != "application/json":
                self._set_headers(415)
                self.wfile.write(
                    json.dumps({"error": "Content must be JSON!"}).encode("utf-8")
                )
                return

            content_length = int(self.headers.get("Content-Length", 0))

            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Content must not be empty"}).encode("utf-8")
                )
                return

            try:
                content = self.rfile.read(content_length)
                data = json.loads(content)

                cleaned_data, error = validate_transaction(data)

                if error:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": error}).encode("utf-8"))
                    return

                data = cleaned_data

                def next_transaction_id():
                    return (
                        max(
                            (
                                int(record["txId"])
                                for record in records
                                if record.get("txId") is not None
                            ),
                            default=0,
                        )
                        + 1
                    )

                new_transaction = {
                    "txId": next_transaction_id(),
                    "categoryID": data["categoryID"],
                    "recipientID": int(data["recipientID"]),
                    "senderID": int(data["senderID"]),
                    "txDate": data["txDate"],
                    "txTime": data["txTime"],
                    "updatedBalance": float(data["updatedBalance"]),
                    "txAmount": float(data["txAmount"]),
                    "txFee": float(data["txFee"]),
                    "currency": data["currency"],
                    "status": data.get("status", "PENDING"),
                }

                records.append(new_transaction)
                save_transactions(records)

                self._set_headers(201)
                self.wfile.write(json.dumps(new_transaction).encode("utf-8"))

            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))

    def do_PUT(self):
        if not self.require_auth():
            return

        records = load_transactions()

        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]

            transaction = next(
                (record for record in records if str(record["txId"]) == transaction_id),
                None,
            )

            if transaction is None:
                self._set_headers(404)
                self.wfile.write(
                    json.dumps({"error": "Transaction not found"}).encode("utf-8")
                )
                return

            content_type = self.headers.get("Content-Type")

            if content_type != "application/json":
                self._set_headers(415)
                self.wfile.write(
                    json.dumps({"error": "Content must be JSON!"}).encode("utf-8")
                )
                return

            content_length = int(self.headers.get("Content-Length", 0))

            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Content must not be empty"}).encode("utf-8")
                )
                return

            try:
                content = self.rfile.read(content_length)
                data = json.loads(content)

                if not isinstance(data, dict):
                    self._set_headers(400)
                    self.wfile.write(
                        json.dumps(
                            {"error": "Request body must be a JSON object"}
                        ).encode("utf-8")
                    )
                    return

                UPDATE_FIELDS = {
                    "categoryID": str,
                    "recipientID": int,
                    "senderID": int,
                    "txDate": str,
                    "txTime": str,
                    "updatedBalance": float,
                    "txAmount": float,
                    "txFee": float,
                    "currency": str,
                    "status": str,
                }

                cleaned_updates = {}

                for key, value in data.items():
                    if key == "txId":
                        self._set_headers(400)
                        self.wfile.write(
                            json.dumps({"error": "txID cannot be changed"}).encode(
                                "utf-8"
                            )
                        )
                        return

                    if key not in UPDATE_FIELDS:
                        self._set_headers(400)
                        self.wfile.write(
                            json.dumps({"error": f"Unknown field: {key}"}).encode(
                                "utf-8"
                            )
                        )
                        return

                    try:
                        cleaned_updates[key] = UPDATE_FIELDS[key](value)
                    except (ValueError, TypeError):
                        self._set_headers(400)
                        self.wfile.write(
                            json.dumps({"error": f"{key} has an invalid value"}).encode(
                                "utf-8"
                            )
                        )

                        return

                for key, value in cleaned_updates.items():
                    transaction[key] = value

                save_transactions(records)

                self._set_headers(200)
                self.wfile.write(json.dumps(transaction).encode("utf-8"))

            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))

    def do_DELETE(self):
        if not self.require_auth():
            return

        records = load_transactions()

        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]

            transaction = next(
                (record for record in records if str(record["txId"]) == transaction_id),
                None,
            )

            if transaction is None:
                self._set_headers(404)
                self.wfile.write(
                    json.dumps({"error": "Transaction not found"}).encode("utf-8")
                )
                return

            records.remove(transaction)
            save_transactions(records)

            self._set_headers(200)
            self.wfile.write(
                json.dumps(
                    {
                        "message": "Transaction deleted successfully",
                        "transaction": transaction,
                    }
                ).encode("utf-8")
            )

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))


def run():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, MomoTxHandler)
    print(f"Starting server on port {server_address[1]}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
