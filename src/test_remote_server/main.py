from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')

mcp = FastMCP('MyExpenseTracker')

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',   
                note TEXT DEFAULT ''
                )
            """
        )

init_db()

@mcp.tool
def add_expenses(date, amount, category, subcategory = "", note = ""):
    '''add new entries into the database'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )

        return {'status': 'ok', 'id': cur.lastrowid}

@mcp.tool
def list_expenses(start_date, end_date):
    '''we can show all the transaction stored in database in a specific date range'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            '''SELECT id, date, amount, category, subcategory, note FROM expenses 
                WHERE date BETWEEN ? and ?
                ORDER BY id ASC''',
                (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool
def summarize(start_date, end_date, category = None):
    '''this tool show the total expenses within a category in a specfic date range'''
    with sqlite3.connect(DB_PATH) as c:
        query = (
            '''
            SELECT category, SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? and ?
            '''
        )
        params = [start_date, end_date]

        if category:
            query += 'AND category = >'
            params.append(category)

        query += 'GROUP BY category ORDER BY category ASC'

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

#start the server
if __name__ =="__main__":
    mcp.run(transport='http', host = "0.0.0.0", port = 8000)