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

```


```
