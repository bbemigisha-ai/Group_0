CREATE DATABASE momosmsDB;
USE momosmsDB;


CREATE TABLE txCategories (
  categoryID VARCHAR(50) PRIMARY KEY,
  categoryName VARCHAR(100),
  description VARCHAR(255)
);

CREATE TABLE Customers (
  customerID INT AUTO_INCREMENT PRIMARY KEY,
  customerName VARCHAR(100),
  phoneNumber VARCHAR(20)
);

CREATE TABLE Transactions (
  txId INT AUTO_INCREMENT PRIMARY KEY,
  categoryID VARCHAR(50),
  recipientID INT,
  senderID INT,
  txDate DATETIME,
  txTime TIME,
  updatedBalance DECIMAL(10,2),
  txAmount DECIMAL(10,2),
  txFee DECIMAL(10,2),
  currency VARCHAR(10),
  status VARCHAR(50),

  FOREIGN KEY (categoryID) REFERENCES txCategories(categoryID),
  FOREIGN KEY (recipientID) REFERENCES Customers(customerID),
  FOREIGN KEY (senderID) REFERENCES Customers(customerID)
);

CREATE TABLE SystemLogs (
  logID INT AUTO_INCREMENT PRIMARY KEY,
  txID INT,
  createdAt DATETIME,
  rawMessage TEXT,

  FOREIGN KEY (txID) REFERENCES Transactions(txId)
);

CREATE TABLE CustomerTransaction (
  customerTxID INT AUTO_INCREMENT PRIMARY KEY,
  customerID INT,
  txID INT,
  role ENUM('sender', 'recipient'),

  FOREIGN KEY (customerID) REFERENCES Customers(customerID),
  FOREIGN KEY (txID) REFERENCES Transactions(txId)
);
