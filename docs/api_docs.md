API DOCUMENTATION

Overview
We developed a REST API for managing mobile money transaction records. The transaction data was originally provided in XML and converted to JSON so the API could access it. We developed it using Python’s built-in http server module. It allows users to view, create, update, and delete transaction records.
The API supports five main operations:
GET 
GET by ID 
POST 
PUT 
DELETE 
The API uses Basic Authentication, meaning you must provide valid login credentials before accessing the transaction data, as provided in our README file.
It runs locally on:  http://localhost:8080
 

##GET Endpoint: View All Transactions
This endpoint returns all the transactions currently stored in the API. The user must provide valid authentication credentials.
For example, when you request:
curl.exe -u "Bertha:bm67" http://localhost:8080/transactions
If the request is successful, the API returns 200:OK , followed by a JSON list of transactions.
A transaction contains information such as:
{
    "txId": 1691,
    "categoryID": "CAT_PAYMENT",
    "recipientID": 5,
    "txAmount": 75000,
    "currency": "RWF",
    "status": "COMPLETED"
}
The actual response contains more fields and multiple transactions.

Possible errors include:

 401 for invalid or missing authentication
 404 for incorrect API path


##GET: View One Transaction
This endpoint is used when the client wants to find one particular transaction.
For example, GET /transactions/1691 searches for the transaction whose txId is 1691.

For example, when you request:
curl.exe -u "Bertha:bm67" http://localhost:8080/transactions/1691

If the transaction exists, the API returns  200 OK,and the transaction information.
If the transaction cannot be found, the API returns 404 Not Found with:
{
    "error": "Transaction couldn't be found"
}


##POST: Add a New Transaction
This is used to create a new transaction. The request must contain JSON data and must include the required transaction fields.
The main required fields are:
categoryID
recipientID
senderID
txDate
txTime
updatedBalance
txAmount
txFee
Currency
The status field is optional. If it is not provided, the API automatically sets it to PENDING.

For example, when you request:
curl.exe -u "Bertha:bm67" -H "Content-Type: application/json" -X POST -d "{\"categoryID\":\"CAT_PAYMENT\",\"recipientID\":5,\"senderID\":10,\"txDate\":\"28 Sep 2026\",\"txTime\":\"21:00:00\",\"updatedBalance\":50000,\"txAmount\":10000,\"txFee\":100,\"currency\":\"RWF\"}" http://localhost:8080/transactions

The API automatically creates the next transaction ID. If the transaction is successfully created, the API returns 201 Created and returns the newly created transaction.

Before creating the transaction, the API checks that:
Required fields have been provided.
Numeric fields contain valid numbers.
The transaction amount is greater than zero.
The transaction fee is not negative.
The request contains valid JSON.

For example, a transaction with txAmount = -5000 will be rejected. The API returns  400 Bad Request


##PUT: Update a Transaction
The PUT endpoint allows an existing transaction to be updated. For example, we can update transaction 1691. The transaction ID itself cannot be changed.
The fields that can be updated include:
categoryID
recipientID
senderID
txDate
txTime
updatedBalance
txAmount
txFee
currency
Status
For Example, we can change the transaction amount and status:
{
    "txAmount": 75000,
    "status": "COMPLETED"
}

Send PUT /transactions/1691. The API returns 200 OK, and the transaction is returned with the updated values. Then use GET to check the same transaction and confirm that the new amount and status have been saved. This is important because it shows that the PUT request did not just return a successful response, the actual transaction data was changed.

The API also checks the update before applying it.
For example, the user cannot change:
{
    "txId": 2000
}
The API returns:
{
    "error": "txId cannot be changed"
}
It also rejects unknown fields and invalid values.


##DELETE: Remove a Transaction
This removes a transaction from the records.
For example:
DELETE /transactions/1691

When you request:
curl.exe -u "Bertha:bm67" -X DELETE http://localhost:8080/transactions/1691
If the transaction exists, the API removes it and returns 200 OK with a message confirming the deletion:
{
    "message": "Transaction deleted successfully"
}
The deleted transaction is also included in the response so that the user can see which record was removed.

After deleting the transaction, when you try to retrieve the same transaction using GET, the API returns 404 Not Found.
This confirms that the transaction had actually been removed.


Data Validation and Error Handling
One of the improvements we made to the API was adding validation so that incorrect data is not stored. The API uses different HTTP status codes depending on the problem.

200
Successful request
GET, PUT, or DELETE

201
Successfully created
POST

400
Bad request
Invalid or missing data

401
Unauthorized
Wrong login credentials

404
Not found
Transaction does not exist

415
Unsupported media type
Request is not JSON
For example, if a request is sent without JSON, the API returns 415 Unsupported Media Type . This helps prevent incorrect data from being added to the system.

##Data Storage
The API uses JSON files to store the transaction records. It first checks for api_transactions.json. If this file exists, it uses it as the API’s main data source. If it does not exist, the API loads the original converted transaction data from transactions.json. When a user creates, updates, or deletes a transaction, the changes are saved back to api_transactions.json. This means that the changes made through the API are not only temporary while the program is running.

