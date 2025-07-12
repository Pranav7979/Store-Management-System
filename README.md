# **Store Management System**

## **Efficiently Manage Your Inventory and Billing\!**

This project provides a simple yet functional Store Management System built with Python's Tkinter for the graphical user interface (GUI) and a MySQL database for data storage. It allows users to manage product inventory, handle billing, and perform basic product operations.

## **Features**

* **User-Friendly GUI:** Intuitive interface developed with Tkinter for easy navigation.  
* **Product Management:**  
  * Add new products with details like Product ID, Name, Quantity, MRP, and Discount.  
  * Edit existing product details.  
  * Remove products from inventory.  
* **Billing System:**  
  * Add products to a bill by Product ID or Name.  
  * Auto-suggest product names during billing.  
  * Update product quantities in the bill.  
  * Remove items from the current bill.  
  * (Placeholder for) Print bill functionality.  
* **Database Integration:** Utilizes MySQL to persistently store inventory and billing data.  
* **Modular Design:** Separates frontend (GUI) and backend (database operations) logic for better maintainability.

## **Prerequisites**

To run this Store Management System, you'll need:

* Python 3.x  
* tkinter (usually comes pre-installed with Python)  
* mysql-connector-python  
* A running MySQL server (e.g., XAMPP, WAMP, or a standalone MySQL installation)  
* A MySQL user with appropriate permissions (e.g., root with password ROOT as configured in backend.py)  
* The icons8-back-arrow-16.png image file for the back button icon.

## **Installation**

1. **Clone the repository (or download the code):**  
   git clone https://github.com/Pranav7979/Store-Management-System  
   cd Store Management System  
2. **Install Python dependencies:**  
   pip install mysql-connector-python

3. **Set up the MySQL Database:**  
   * Ensure your MySQL server is running.  
   * Connect to your MySQL server (e.g., using MySQL Workbench, command line, or phpMyAdmin).  
   * Create a database named inventory\_records:  
     CREATE DATABASE inventory\_records;  
     USE inventory\_records;

   * Create the inventory table:  
     CREATE TABLE inventory (  
         \`Product ID\` INT PRIMARY KEY,  
         \`Product Name\` VARCHAR(255) NOT NULL,  
         \`Quantity\` INT NOT NULL,  
         \`MRP\` DECIMAL(10, 2\) NOT NULL,  
         \`Discount (%)\` DECIMAL(5, 2),  
         \`Selling Price\` DECIMAL(10, 2\) AS (MRP \- (MRP \* \`Discount (%)\` / 100))  
     );

   * Create the billing table:  
     CREATE TABLE billing (  
         \`Product ID\` INT,  
         \`Product Name\` VARCHAR(255),  
         \`Quantity\` INT,  
         \`MRP\` DECIMAL(10, 2),  
         \`Rate\` DECIMAL(10, 2\)  
     );

   * **Important:** The backend.py file uses user \= 'root', password \= 'ROOT'. If your MySQL setup uses different credentials, you will need to modify the connect\_db() function in backend.py accordingly.  
4. Place the back arrow icon:  
   Ensure the icons8-back-arrow-16.png file is in the same directory as your frontend\_2\_0.py script.

## **How to Run**

1. Navigate to the project directory in your terminal.  
2. Run the frontend script:  
   python frontend\_2\_0.py

## **How to Use**

* **Dashboard (Home Page):**  
  * **BILLING:** Click to go to the billing interface.  
  * **PRODUCT:** Click to go to the product management interface.  
  * **ORDERS / ANALYSIS:** (Currently placeholders) These buttons are for future expansion.  
* **Billing Page:**  
  * **Add New Item:** Enter Product ID or Product Name (with auto-suggestions), and the system will add it to the bill.  
  * **Update Quantity:** Select an item in the bill table, enter a new quantity in the "Quantity" field, and click "Update Quantity". Entering 0 will delete the item.  
  * **Delete Selected Item:** Select an item in the bill table and click this button to remove it.  
  * **Print:** (Placeholder) For generating a bill summary.  
* **Products Page:**  
  * **Add Product:** Opens a dialog to enter details for a new product (ID, Name, Quantity, MRP, Discount).  
  * **Edit Product:** Opens a dialog to modify details of an existing product.

## **Contributing**

Contributions to this project are welcome\! Feel free to:

* Report bugs  
* Suggest new features  
* Submit pull requests

## **Acknowledgments**

* [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework.  
* [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/) for MySQL database connectivity.  
* [icons8](https://icons8.com/) for the back arrow icon.