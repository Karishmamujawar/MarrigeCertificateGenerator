import sqlite3 


con = sqlite3.connect("database.db")
cur = con.cursor()


# cur.execute(''' 
#         CREATE TABLE IF NOT EXISTS info (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         gname TEXT NOT NULL,
#         bname TEXT NOT NULL,
#         mrg_date TEXT ,
#         place TEXT NOT NULL

# )
#             ''')    


cur.execute(''' 
    ALTER TABLE info DROP COLUMN temp;
     
''')

con.commit()
con.close()