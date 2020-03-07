import sqlite3
conn = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
conn.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, owner char(100) NOT NULL, task char(100) NOT NULL, status bool NOT NULL)")
conn.execute("INSERT INTO todo (owner,task,status) VALUES ('user0','Read A-byte-of-python to get a good introduction into Python',0)")
conn.execute("INSERT INTO todo (owner,task,status) VALUES ('user0','Visit the Python website',1)")
conn.execute("INSERT INTO todo (owner,task,status) VALUES ('user0','Test various editors for and check the syntax highlighting',1)")
conn.execute("INSERT INTO todo (owner,task,status) VALUES ('user0','Choose your favorite WSGI-Framework',0)")
conn.commit()

conn = sqlite3.connect('users.db') # Warning: This file is created in the current directory
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name char(100) NOT NULL, password char(100) NOT NULL)")
conn.execute("INSERT INTO users (name,password) VALUES ('therock','alcatraz')")
conn.execute("INSERT INTO users (name,password) VALUES ('schatzi','mausi')")
conn.commit()