# Group_0 — MoMo SMS Data Analytics

## Project Description

This project takes MoMo (Mobile Money) SMS data in XML format, cleans it up, and organizes it into categories. The clean data is stored in a database and shown on a simple dashboard so we can analyze and visualize it.

## Team Members

- Bemigisha Bertha Mbonimpa
- Kirabo Karyna Kiwagama
- Nadiv Gicheru

## Team Task Sheet

https://docs.google.com/spreadsheets/d/1CQbXaVT_BGN0rENaPyD16J1KZtcKcp_oXJ-TXU_im1Y/edit?usp=sharing

## Scrum Board

Track our tasks (To Do / In Progress / Done): _https://trello.com/b/BhmRjvQo/group-0-momo-sms_

## SQL - JSON Mapping Table

| **Entity**              | **JSON Field** | **SQL Field**                    |
| ----------------------- | -------------- | -------------------------------- |
| **Transactions**        | txID           | transaction.txId                 |
|                         | categoryID     | transaction.category.categoryID  |
|                         | senderID       | transaction.sender.customerID    |
|                         | recipientID    | transaction.recipient.customerID |
| **Customers**           | customerID     | sender.customerID                |
|                         |                | recipient.customerID             |
|                         | customerName   | sender.customerName              |
|                         |                | recipient.customerName           |
|                         | phoneNumber    | sender.phoneNumber               |
|                         |                | recipient.phoneNumber            |
| **txCategories**        | categoryID     | category.categoryID              |
|                         | categoryName   | category.categoryName            |
| **SystemLogs**          | logID          | systemLogs.logID                 |
|                         | rawMessage     | systemLogs.rawMessage            |
| **CustomerTransaction** | role           | sender.role                      |
|                         |                | recipient.role                   |

## Running the API

1. Clone the API:
   `git clone https://github.com/bbemigisha-ai/Group_0.git`

2. From the directory run:
   ` python etl/main.py`
   or
   ` python3 etl/main.py - if you're using macOS`

The server runs at:

http://localhost:8080

The API reads the parsed transaction data in data/converted_transactions/api_transactions.json

## Authentication

All endpoints require HTTP Basic Auth

for testing you could use:
| **Username** | **Password** |
| ----------------------- |----|
| **karyna** | kk89|
| **bertha** | bm67 |
| **nadiv** | ng25 |
| **Guest** | ng25 |

It's important to note that Basic Auth must be used over HTTPS in production and Base64 does not actually encrypt credentials. For stronger security we recommend implementing alternatives that are stronger i.e. OAuth2

## Reference Table for Endpoints

```markdown
## Endpoints

| Method | Endpoint             | Description                    | Success |
| ------ | -------------------- | ------------------------------ | ------- |
| GET    | `/transactions`      | List all transactions          | 200     |
| GET    | `/transactions/{id}` | Get one transaction            | 200     |
| POST   | `/transactions`      | Create a transaction           | 201     |
| PUT    | `/transactions/{id}` | Partially update a transaction | 200     |
| DELETE | `/transactions/{id}` | Delete a transaction           | 200     |
```

## Request, Response & Tests

For test examples of the different requests and their responses, please see `screenshots/api_requests`

## Validation and Error Codes

```markdown
## Validation and Errors

| Status | Meaning                                         |
| ------ | ----------------------------------------------- |
| 200    | Successful GET, PUT, or DELETE                  |
| 201    | Transaction created                             |
| 400    | Invalid JSON, missing fields, or invalid values |
| 401    | Missing or invalid credentials                  |
| 404    | Transaction or route not found                  |
| 415    | Request body is not JSON                        |

Transactions must have a positive amount, a non-negative fee, valid numeric IDs,
and valid JSON fields.
```

For some test examples, please see `screenshots/api_requests`

- Some other tested behaviours include:
- Successful authentication
- Invalid and malformed authentication
- Listing transactions
- Retrieving one transaction
- Creating a transaction
- Updating a transaction
- Deleting a transaction
- Persistence after restarting the server
- Invalid JSON and invalid field values
