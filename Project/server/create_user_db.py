#!/usr/bin/env python3
import hashlib, os, sqlite3

def HashPass(password=''):
    if not password:
        return None
    return str(hashlib.sha512(password.encode('utf-8')).hexdigest())

class Database():
    def __init__(self, name, wipe=True):
        self.path = os.path.join(os.getcwd(), name)
        if wipe and os.path.exists(self.path):
            os.remove(self.path)
        
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
    
    def Close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def CreateTable(self, name='', cols=()):
        if self.cursor and name and len(cols) > 0:
            col_str = ', '.join(cols)
            query = 'CREATE TABLE IF NOT EXISTS ' + str(name) + ' (' + col_str + ');'
            print(query)
            self.cursor.execute(query)
    
    def AddItem(self, table_name='', cols=()):
        if self.cursor and table_name and len(cols) > 0:
            col_str = ', '.join(['?'] * len(cols))
            query = 'INSERT INTO ' + table_name + ' VALUES (' + col_str + ');'
            print(query)
            self.cursor.execute(query, cols)
    
    def PrintTable(self, table_name=''):
        if self.cursor and table_name:
            for row in self.cursor.execute('SELECT * FROM ' + str(table_name) + ';'):
                print(row)

users = Database('users.db')

users.CreateTable('users', (
    'UID INTEGER PRIMARY KEY CHECK (UID >= 0)',
    'USER TEXT NOT NULL UNIQUE',
    'PASS TEXT NOT NULL'
))

users.AddItem('users', (0, 'admin', HashPass('password')))
users.AddItem('users', (1, 'john', HashPass('feb123')))

users.PrintTable('users')
users.Close()
