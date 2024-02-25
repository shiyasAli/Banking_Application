import mysql.connector
import re
import pandas as pd


def insert_values(database_name, table_name, column_names, values):
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root' , 
            password = '',
            database = database_name
        )

        cursor = connection.cursor()

        columns = ', '.join(column_names)
        placeholder = ', '.join(['%s']*len(values))
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholder})'

        cursor.execute(query, values)
        connection.commit()
        print('insertion successful')

    except mysql.connector.Error as err:
        print('Error:', err)

    finally:
        cursor.close()
        connection.close()

def execute_query(database_name, query):
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = database_name
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return rows, columns
    
    except mysql.connector.Error as e:
        print('Error:', e)
        return None

    finally:
        cursor.close()
        connection.close()

def update_table(database_name, query):
    connection = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = database_name
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query)
        connection.commit()

    except mysql.connector.Error as err:
        print('Error updating table: ', err)

    finally:
        cursor.close()
        connection.close()
    


def register_user():
    print('Enter first name')
    first_name = input()
    print('Enter last name')
    last_name = input()
    print('Enter user name')
    user_name = input()
    while True:
        query = f'select * from users where user_name = "{user_name}" '
        rows = execute_query('banking_app', query)[0]
        if len(rows) == 0:
            print('user name created succesfully')
            break
        else:
            print('user name already taken. Enter a different username')
            user_name = input()
    print('Enter house name')
    house_name = input()
    print('Enter house number.')
    house_num = input()
    print('Enter area.')
    area = input()
    print('Enter city.')
    city = input()
    print('Enter state.')
    state = input()
    print('Enter pincode')
    pin_code = input()
    print('Enter mobile number')
    mobile_number = input()
    
    while True:
        pattern = r'^\d{10}$'
        if not bool(re.match(pattern, mobile_number)):
            print('please enter a valid mobile number')
            mobile_number = input()
            continue
        else:
            query = f'select * from users where mobile_number = "{mobile_number}"'
            rows = execute_query('banking_app', query)[0]
            if len(rows) == 0:
                print('Mobile number added successfully.')
                break
            else:
                print('Same mobile number exists for a different user. Pick new mobile number.')
                mobile_number = input()
    
    print('Enter Aadhar number.')
    aadhar_number = input()

    while True:
        pattern = r'^\d{12}$'
        if not bool(re.match(pattern, aadhar_number)):
            print('Enter valid Aadhar number')
            aadhar_number = input()
            continue
        else:
            query = f'select * from users where aadhar_number = "{aadhar_number}"'
            rows = execute_query('banking_app', query)[0]
            if len(rows) == 0:
                print('Aadhar number added successfully')
                break
            else:
                print('Same Aadhar number exists for a different user. Pick new Aadhar number.')
                aadhar_number = input()
    
    print('Choose a password')
    password = input()

    columns = ['first_name', 'last_name', 'user_name', 'house_name', 'house_num', 'area',  'city', 'state', 'pin_code', 'mobile_number', 'aadhar_number']
    values = [first_name, last_name, user_name, house_name, house_num, area,  city, state, pin_code, mobile_number, aadhar_number]
    insert_values('banking_app', 'users', columns, values)

    columns = ['user_name', 'password']
    values = [user_name, password]
    insert_values('banking_app', 'password', columns, values)

def add_beneficiary(account_no):
    account_no = int(account_no)
    
    print('Enter beneficiary name.')
    beneficiary = input()
    columns = ['account_no', 'beneficiary_name']
    values = [account_no, beneficiary]

    insert_values('banking_app', 'beneficiary', columns, values)

def transaction(account_no):
    account_no = int(account_no)
    
    print('Enter account number.')
    r_acc_no = int(input())
    print('Enter amount')
    amount = int(input())

    columns = ['from_account_no', 'to_account_no', 'amount']
    values = [account_no, r_acc_no, amount]

    insert_values('banking_app', 'transactions', columns, values)

    query = f'update accounts set balance = balance -{amount} where account_no = {account_no}'
    update_table('banking_app',query)

    query = f'update accounts set balance = balance + {amount} where account_no = {r_acc_no}'
    update_table('banking_app',query)

def deposit(account_no):
    account_no = int(account_no)
    
    print('Enter amount to deposit.')
    amount = int(input())

    query = f'update accounts set balance = balance + {amount} where account_no = {account_no}'
    update_table('banking_app',query)

def change_mpin(account_no):
    account_no = int(account_no)
    
    print('Enter card number.')
    card_no = int(input())
    print('Enter new mpin.')
    mpin = input()

    pattern = r'^\d{4}$'

    while True:
        if not bool(re.findall(pattern, mpin)):
            print('Mpin should be a 4 digit number. Enter new Mpin.')
            mpin = input()
            continue
        else:
            query = f'update credit_cards set pin = {int(mpin)} where account_no = {account_no} and card_no = {card_no}'
            update_table('banking_app',query)

            print('Mpin changed successfully.')
            break

def register_new_card(account_no):
    account_no = int(account_no)
    
    columns = ['account_no']
    values = [account_no]

    insert_values('banking_app', 'credit_cards', columns, values)
    print('Credit carded added successfully.')

def sign_in_page():
    print('Enter 1 to register new account.')
    print('Enter 2 to login to your account.')

    choice = int(input())

    if choice == 1:
        register_user()
    elif choice == 2:
        login()
    else:
        print('Wrong input. Try again.')
        sign_in_page()

    
def home_page(user_name):
    query = f'select a.user_id, b.account_no, b.balance from users a join accounts b on a.user_id = b.user_id where user_name = "{user_name}"'
    rows, columns = execute_query('banking_app', query)

    user_account_df = pd.DataFrame(rows, columns = columns)

    account_no = user_account_df.iloc[0,1]
    balance = user_account_df.iloc[0,2]

    
    query = f'select * from credit_cards where account_no = {account_no}'
    rows, columns = execute_query('banking_app', query)
    credit_card_df = pd.DataFrame(rows, columns = columns)

    query = f'select * from debit_cards where account_no = {account_no}'
    rows, columns = execute_query('banking_app', query)
    debit_card_df = pd.DataFrame(rows, columns = columns)

    query = f'select * from beneficiary where account_no = {account_no}'
    rows, columns = execute_query('banking_app', query)
    beneficiary_df = pd.DataFrame(rows, columns= columns)

    print('Account number: ', account_no)
    print('Balance: ', balance)
    print('Benificiaries: ', list(beneficiary_df['beneficiary_name']))
    print('Debit card number: ', list(debit_card_df['card_no']))
    print('Credit card number: ', list(credit_card_df['card_no']))
    print('Enter 1 to add beneficiary.')
    print('Enter 2 to transfer fund.')
    print('Enter 3 to deposit money')
    print('Enter 4 to change mpin of your credit card.')
    print('Enter 5 to register new credit card.')
    print('Enter 6 to logout.')

    choice = int(input())

    if choice == 1:
        add_beneficiary(account_no)
        home_page(user_name)
    elif choice == 2:
        transaction(account_no)
        home_page(user_name)
    elif choice == 3:
        deposit(account_no)
        home_page(user_name)
    elif choice == 4:
        change_mpin(account_no)
        home_page(user_name)
    elif choice == 5:
        register_new_card(account_no)
        home_page(user_name)
    elif choice == 6:
        sign_in_page()
    else:
        print('Wrong input. Try again.')
        home_page(user_name)
    







def login():
    print('Enter user name.')
    user_name = input()
    print('Enter password.')
    password = input()

    while True:
        query = f'select * from password where user_name = "{user_name}" and password = "{password}"'
        row = execute_query('banking_app', query)[0]

        if len(row) == 0:
            print('User name and password does not match.')
            
            print('Enter user name.')
            user_name = input()
            print('Enter password.')
            password = input()
            continue

        else:
            print('Login successful.')
            break
    home_page(user_name)

sign_in_page()





    

    







