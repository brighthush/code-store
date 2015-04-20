"""This module showed how to use mongo db in python.
I packaged the mongo db api in my own style.
"""
#coding=utf8

import pymongo

class Mongo:
    def __init__(self, host='localhost', port=27017, db='center', col='test'):
        self.conn = pymongo.Connection(host, port)
        self.db = self.conn[db]
        self.coll = self.db[col]

    def show_collections(self):
        colls = self.db.collection_names()
        return colls

    def insert(self, doc):
        """doc is a dict
        """
        self.coll.insert(doc)

    def find(self, condition=None):
        """condition is a dict
        """
        if condition==None:
            return self.coll.find()
        else:
            return self.coll.find(condition)

    def update(self, condition, updates):
        """condition and updates are all dict, condition is to
        find the documents you want to update, updates is the key-val pairs
        which you want to reset.
        """
        self.coll.update(condition, {'$set':updates})

    def show_documents(self):
        lines = self.find()
        for line in lines:
            print line

def main():
    mongo = Mongo()
    mongo.show_documents()


if __name__ == '__main__':
    main()

