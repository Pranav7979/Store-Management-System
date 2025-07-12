import mysql.connector as ct

def connect_db():
    mydb = ct.connect(user = 'root', password = 'ROOT', host = 'localhost', database = 'inventory_records', autocommit = True)
    return mydb


def print_table(mydb,table_name):
    mycursor = mydb.cursor()
    query = f"SELECT * FROM {table_name}"
    mycursor.execute(query)
    results = mycursor.fetchall()

    col_name = [i[0] for i in mycursor.description]
    print(*col_name, sep=", ")
    print(results)

    # for row in results:
    #     print(*row, sep=", ")
    
    mycursor.close()
    return results



def add_new_product(mydb,input_list):
    input_tuple = tuple(input_list)

    mycursor = mydb.cursor()
    query = f"SELECT COUNT(*) FROM `inventory` WHERE `Product ID` = {input_list[0]}"
    mycursor.execute(query)
    result = mycursor.fetchone()[0]

    if not result:
        query = f"INSERT INTO `inventory` (`Product ID`, `Product Name`, `Quantity`, `MRP`, `Discount (%)`) VALUES {input_tuple}"
        mycursor.execute(query)
        mydb.commit()

    else:
        print(f"Product ID {input_list[0]} already exists.")

    mycursor.close()



def remove_product(mydb, table, id):
    mycursor = mydb.cursor()
    query = f"SELECT COUNT(*) FROM `{table}` WHERE `Product ID` = %s"
    mycursor.execute(query, (id,))
    result = mycursor.fetchone()[0]

    if result:
        query = f"DELETE FROM `{table}` WHERE `Product ID` = %s"
        mycursor.execute(query, (id,))
        mydb.commit()
        print("Deleted!")

    else:
        print("Does not exist!")

    mycursor.close()



def edit_product(mydb, prev_id, li):
    # li = tuple(new_val)
    mycursor = mydb.cursor()
    query = f"SELECT COUNT(*) FROM `inventory` WHERE `Product ID` = {prev_id}"
    mycursor.execute(query)
    result = mycursor.fetchone()[0]

    if result:
        query = f"UPDATE `inventory` SET `Product ID` = %s, `Product Name` = %s, `Quantity` = %s, `MRP` = %s, `Discount (%)` = %s WHERE `Product ID` = %s"
        value = (li[0], li[1], li[2], li[3], li[4], prev_id)
        mycursor.execute(query, value)
        mydb.commit()
        print("Updated!")

    else:
        print("Does not exist!")
    
    mycursor.close()



def fetch_prod(mydb, prod_id):
    mycursor = mydb.cursor()
    query = f"SELECT `Product ID`, `Product Name`, `Quantity`, `MRP`, `Selling Price` FROM `inventory` WHERE `Product ID` = {prod_id}"
    mycursor.execute(query)
    results = mycursor.fetchall()
    return results



def add_to_bill(mydb, prod_id=0, prod_name='NULL'):
    mycursor = mydb.cursor()

    query = f"SELECT `Quantity` FROM `billing` WHERE (`Product ID` = %s) OR (`Product Name` = %s)"
    mycursor.execute(query, (prod_id, prod_name))
    results = mycursor.fetchall()
    print(results[0][0])
    if results:
        print("hi")
        # results = mycursor.fetchall()
        qty = 1 + results[0][0]
        query = f"UPDATE `billing` SET `Quantity` = %s WHERE (`Product ID` = %s) OR (`Product Name` = %s)"
        mycursor.execute(query, (qty, prod_id, prod_name))
        mydb.commit()
        mycursor.close()
        return


    if prod_id!=0:
        query = f"SELECT `Product ID`, `Product Name`, `Quantity`, `MRP`, `Selling Price` FROM `inventory` WHERE `Product ID` = {prod_id}"
        mycursor.execute(query)
    elif prod_name!='NULL':
        query = f"SELECT `Product ID`, `Product Name`, `Quantity`, `MRP`, `Selling Price` FROM `inventory` WHERE `Product Name` = %s"
        mycursor.execute(query, (prod_name,))
    else:
        return

    # mycursor.execute(query)
    results = mycursor.fetchall()
    li = [item for val in results for item in val]
    li[2] = 1

    query = f"INSERT INTO `billing` (`Product ID`, `Product Name`, `Quantity`, `MRP`, `Rate`) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(query, li)
    mydb.commit()
    # return results


def suggest_prod(mydb):
    mycursor = mydb.cursor()
    query = f"SELECT `Product Name` FROM `inventory`"
    mycursor.execute(query)
    results = mycursor.fetchall()
    names = [item for li in results for item in li]
    # for li in results:
    #     names.append(li)
    print(names)
    return names


def update_quantity(mydb, table, id, quantity):
    mycursor = mydb.cursor()
    query = f"UPDATE `{table}` SET `Quantity` = %s WHERE `Product ID` = %s"
    mycursor.execute(query, (quantity, id))



# def add_to_cart():


# def remove_from_cart():


# def finalize_order():


# li = [1,'n',1,10,10]
# add_new_product(li)

# remove_product(connect_db(), 'billing', 103)

# edit_product(2,li)

# print_table(connect_db(),'inventory')
# fetch_prod(connect_db(),101)
# add_to_bill(connect_db(), prod_id=103)

def close_db(mydb):
    mydb.close()