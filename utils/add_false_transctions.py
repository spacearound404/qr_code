import os
import random
import config
import sqlite3

max_count = 20
user_email = ""

conn = sqlite3.connect(config.NAME_DB, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS 'users' (
	'id'	INTEGER,
	'email'	TEXT UNIQUE,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS 'images' (
	'id'	INTEGER,
	'file_name'	TEXT UNIQUE,
	'is_sent'	INTEGER,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS 'transactions' (
	'id'	INTEGER,
	'charge_hosted_url'	TEXT,
	'charge_id'	TEXT,
	'charge_code'	TEXT,
	'images_count'	INTEGER,
	'item_price'	INTEGER,
	'amount'	INTEGER,
	'status'	TEXT,
	'user_id'	INTEGER,
	'images_id_arr'	TEXT,
    'blockchain_trans_id' TEXT,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

files = os.listdir(config.IMAGES_FOLDER)

i = 0
user_id = 0
files_list = []

for file in files:
    if i < max_count:
        files_list.append(file)

        # update is_sent in images by id
        cursor.execute("UPDATE images SET is_sent = 1 WHERE file_name = ?;", (file,)) 
        conn.commit()

    i += 1

cursor.execute("SELECT * FROM users WHERE email = ?;", (user_email,))
res = cursor.fetchone()

# if email isn't there then insert new row
if res is None:
    cursor.execute("INSERT INTO users(email) VALUES(?);", (user_email,))
    conn.commit()
else:
    user_id = res[0]

cursor.execute("INSERT INTO transactions(charge_hosted_url, charge_id, charge_code, images_count, item_price, amount, status, user_id, images_id_arr) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", ("none", -1, "none", max_count, 1, max_count, "confirmed", user_id, str(files_list)))
conn.commit()
