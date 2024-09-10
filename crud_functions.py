import sqlite3

product_name_list = ['Omega-3', 'Vitamins complex', 'PRO BIOTICS', 'Turbo Tea']
description_list = ['Витаминки с Омегой-3, типа для веганов',
                    'Витаминки A, C, E',
                    'Живые микроорганизмы, приносящие пользу хозяину',
                    'Слабительное под видом чая']


def connection_session(func):

    def wrapper(*args):
        connection = sqlite3.connect("My_shop.db")
        cursor = connection.cursor()
        result = func(*args, cursor=cursor)
        connection.commit()
        connection.close()
        return result
    return wrapper


@connection_session
def initiate_db(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
        )
    """)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER NOT NULL,
    balance INTEGER NOT NULL
    )
    ''')


@connection_session
def add_user(username, email, age, cursor):
    check_user = cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    if check_user.fetchone() is None:
        cursor.execute("SELECT MAX(id) FROM Users")
        last_id = cursor.fetchone()[0]
        if last_id is None:
            last_id = 0
        cursor.execute(f'''
        INSERT INTO Users VALUES('{last_id + 1}', '{username}', '{email}', '{age}', 1000)
        ''')


@connection_session
def is_included(username, cursor):
    check_user = cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    if check_user.fetchone() is None:
        return False
    return True


@connection_session
def get_all_products(cursor):
    cursor.execute('SELECT * FROM Products')
    return cursor.fetchall()


@connection_session
def setup(cursor):
    for i in range(1, 5):
        cursor.execute('INSERT INTO Products(id, title, description, price) VALUES(?, ?, ?, ?)',
                       (f'{i}', f'{product_name_list[i - 1]}', f'{description_list[i - 1]}', i * 100))
