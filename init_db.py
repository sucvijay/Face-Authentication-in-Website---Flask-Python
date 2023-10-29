import sqlite3


connection = sqlite3.connect("sqlite.db")

with open("schema.sql") as f:
    connection.executescript(f.read())
    
    
# connection.row_factory = sqlite3.Row


    



