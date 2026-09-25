import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import base64

transactions = []


class MomoTxHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET_allTransactions(self):
        if self.path == "/transactions":
            self._set_headers(200)
            self.wfile.write(json.dumps(transactions).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))

    def do_GET_oneTransaction(self):
        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]
            transaction = next(
                (t for t in transactions if str(t["id"]) == transaction_id), None
            )
            if transaction:
                self._set_headers(200)
                self.wfile.write(json.dumps(transaction).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(
                    json.dumps({"error": "Transaction not found"}).encode("utf-8")
                )
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Path not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/transactions":
            content_type = self.headers.get("Content-Type")
            if content_type != "application/json":
                self._set_headers(415)
                self.wfile.write(
                    json.dumps({"error": "Content must be JSON!"}).encode("utf-8")
                )

            content_length = int(self.headers.get("Content-Length", 0))

            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Content must not be empty"}).encode("utf-8")
                )

            try:
                content = self.rfile.read(content_length)
                data = json.loads(content)

                new_transaction = {
                    "txId": len(transactions) + 1,
                    "categoryID": data.get("categoryID", "Unkown"),
                    "recipientID": data.get("recipientID", "Unknown"),
                    "senderID": data.get("senderID", "Unknown"),
                    "txDate": data.get("txDate", "Unknown"),
                    "txTime": data.get("txTime", "Unknown"),
                    "updatedBalance": data.get("updateBalance", "Unknown"),
                    "txAmount": data.get("txAmount", "Unknown"),
                    "txFee": data.get("txFee", "Unknown"),
                    "currency": data.get("currency", "Unknown"),
                    "status": "pending",
                }

                transactions.append(new_transaction)

                self._set_headers(201)
                self.wfile.write(json.dumps(new_transaction).encode("utf-8"))

            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))

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
