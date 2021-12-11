import os
import random
import config
import sqlite3

conn = sqlite3.connect(config.NAME_DB, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS 'images' (
	'id'	INTEGER,
	'file_name'	TEXT UNIQUE,
	'is_sent'	INTEGER,
	PRIMARY KEY('id' AUTOINCREMENT)
);""")

files = os.listdir(config.IMAGES_FOLDER)

for file in files:
    new_file_name = str(random.randint(1000, 9999)) + "-" + str(random.randint(1000, 9999)) + "-" + str(random.randint(1000, 9999)) + "-" + str(random.randint(1000, 9999)) + ".jpg"
    os.rename(config.IMAGES_FOLDER + file, config.IMAGES_FOLDER + new_file_name)

    cursor.execute("INSERT INTO images(file_name, is_sent) VALUES(?, ?);", (new_file_name, 0))
    conn.commit()

cursor.execute("SELECT * FROM images;")
res = cursor.fetchall()

print(res)
