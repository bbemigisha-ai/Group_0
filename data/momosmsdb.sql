DROP DATABASE IF EXISTS momosmsDB;
CREATE DATABASE momosmsDB;
USE momosmsDB;


CREATE TABLE txCategories (
  categoryID VARCHAR(50) PRIMARY KEY,
  categoryName VARCHAR(100) NOT NULL,
  description VARCHAR(255)
);

CREATE TABLE customers (
  customerID INT AUTO_INCREMENT PRIMARY KEY,
  customerName VARCHAR(100) NOT NULL,
  phoneNumber VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE transactions (
  txId INT AUTO_INCREMENT PRIMARY KEY,
  categoryID VARCHAR(50) NOT NULL, 
  recipientID INT NOT NULL,
  senderID INT NOT NULL,
  txDate DATETIME NOT NULL,
  updatedBalance DECIMAL(10,2) NOT NULL,
  txAmount DECIMAL(10,2) CHECK (txAmount > 0),
  txFee DECIMAL(10,2) CHECK (txFee >= 0),
  currency VARCHAR(10) CHECK (currency IN ('RWF')), -- Only dealing with Rwandan Francs
  status VARCHAR(50) CHECK (status IN ('SUCCESS', 'FAILED', 'REVERSED')),

  CHECK (senderID <> recipientID), -- Prevent customer transacting with themselves

  FOREIGN KEY (categoryID) REFERENCES txCategories(categoryID),
  FOREIGN KEY (recipientID) REFERENCES Customers(customerID),
  FOREIGN KEY (senderID) REFERENCES Customers(customerID)
);

CREATE TABLE systemLogs (
  logID INT AUTO_INCREMENT PRIMARY KEY,
  txID INT NOT NULL,
  createdAt DATETIME NOT NULL,
  rawMessage TEXT NOT NULL,

  FOREIGN KEY (txID) REFERENCES transactions(txId)
);

CREATE TABLE customerTransaction (
  customerTxID INT AUTO_INCREMENT PRIMARY KEY,
  customerID INT NOT NULL,
  txID INT NOT NULL,
  role ENUM('sender', 'recipient') NOT NULL,

  FOREIGN KEY (customerID) REFERENCES Customers(customerID),
  FOREIGN KEY (txID) REFERENCES transactions(txId),
  UNIQUE KEY uq_customer_tx_role (customerID, txID, role) 
  -- prevents customer holding a role on the same transaction twice, but they can appear across multiple transactions
);

-- SAMPLE QUERIES -- 

INSERT INTO txCategories (categoryID, categoryName, description)
VALUES ('DEP', 'Deposit', 'Funds added to account');

INSERT INTO customers (customerName, phoneNumber)
VALUES ('Oscar Isaac', '0759674567');

INSERT INTO customers (customerName, phoneNumber)
VALUES ('Karyna Kirabo', '0744089764');

INSERT INTO transactions (
    categoryID, recipientID, senderID, txDate,
  updatedBalance, txAmount, txFee, currency, status
)
VALUES (
    'DEP', 2, 1, NOW(), 25000.00, 5000.00, 100.00, 'RWF', 'SUCCESS'
);


INSERT INTO customerTransaction (customerID, txID, role)
VALUES (1, 1, 'sender');

INSERT INTO customerTransaction (customerID, txID, role)
VALUES (2, 1, 'recipient');


-- show transactions with actual names. Join info from customers and transaction
SELECT t.txID, s.customerName AS sender, r.customerName AS recipient, t.txAmount, t.currency, t.status
FROM transactions t
JOIN customers s ON t.senderID = s.customerID
JOIN customers r ON t.recipientID = r.customerID;

-- filter by transaction status
SELECT txId, txAmount, txDate
FROM transactions
WHERE status = 'SUCCESS';


-- full transaction via junction TABLE

SELECT cu.customerName, ct.role, t.txId, t.txAmount
FROM customerTransaction ct
JOIN customers cu ON ct.customerID = cu.customerID
JOIN transactions t ON ct.txID = t.txID
WHERE cu.customerID = 1;


-- test rules
-- 1. Sender cannot send to themselves
INSERT INTO transactions (
    categoryID, recipientID, senderID, txDate,
  updatedBalance, txAmount, txFee, currency, status
)
VALUES (
    'DEP', 1, 1, NOW(), 25000.00, 5000.00, 100.00, 'RWF', 'SUCCESS'
);


-- 2. Cannot have negative amount transacted

INSERT INTO transactions(     categoryID, recipientID, senderID, txDate,
  updatedBalance, txAmount, txFee, currency, status
)
VALUES (
    'DEP', 1, 1, NOW(), -25000.00, 5000.00, 100.00, 'RWF', 'SUCCESS'
);
