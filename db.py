import sqlite3

def connect():
    db = sqlite3.connect('database')
    init_db(db)
    return db

def init_db(db):
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS tells(receiver, message)')

def save_tell(db, receiver, message):
    cursor = db.cursor()
    cursor.execute('INSERT INTO tells(receiver, message) VALUES(?,?)',
                    (receiver, message))
    db.commit()
    return


def delete_tells(db, receiver):
    cursor = db.cursor()
    cursor.execute('DELETE from tells WHERE receiver = ?', (receiver,))
    db.commit()
    return


def get_tells(db, receiver):
    '''Returns a list of rows representing "tells"'''
    cursor = db.cursor()
    rows = cursor.execute('SELECT receiver, message FROM tells').fetchall()
    tells = [row for row in rows if receiver in row[0]]
    delete_tells(db, receiver)
    return tells

