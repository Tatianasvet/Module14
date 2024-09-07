import sqlite3

product_name_list = ['Omega-3', 'Vitamins complex', 'PRO BIOTICS', 'Turbo Tea']
description_list = ['Витаминки с Омегой-3, типа для веганов',
                    'Витаминки A, C, E',
                    'Живые микроорганизмы, приносящие пользу хозяину',
                    'Слабительное под видом чая']


def initiate_db():
    connection = sqlite3.connect("Products.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def get_all_products():
    connection = sqlite3.connect("Products.db")
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Products')
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def setup():
    connection = sqlite3.connect("Products.db")
    cursor = connection.cursor()
    for i in range(1, 5):
        cursor.execute('INSERT INTO Products(id, title, description, price) VALUES(?, ?, ?, ?)',
                       (f'{i}', f'{product_name_list[i - 1]}', f'{description_list[i - 1]}', i * 100))
    connection.commit()
    connection.close()
