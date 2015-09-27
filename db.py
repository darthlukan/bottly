import sqlite3


def connect():
    db = sqlite3.connect('database')
    return db


def save_tell(db, reciever, message):
    cursor = db.cursor()
    cursor.exectute('INSERT INTO tells(reciever, message) VALUES(?,?)',
                    (reciever, message))
    db.commit()
    return


def delete_tells(db, receiver):
    cursor = db.cursor()
    cursor.execute('DELETE from tells WHERE reciever = ?', (receiver,))
    db.commit()
    return


def get_tells(db, receiver):
    '''Returns a list of rows representing "tells"'''
    cursor = db.cursor()
    rows = cursor.execute('SELECT reciever, message').fetchall()
    tells = [row for row in rows if receiver in row[0]]
    delete_tells(db, receiver)
    return tells

