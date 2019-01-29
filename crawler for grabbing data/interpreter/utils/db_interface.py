import logging
import pymongo

# Specify your MongoDB connection here, if not default
DB_CONNECT = {"host" : "localhost", "port" : 27017}


def get_connect_path():
    connect_path = "mongodb://{}:{}/".format(DB_CONNECT["host"], DB_CONNECT["port"])
    return connect_path


class DBHandler:
    def __init__(self, db_name, log_handler=None):
        """Constructor

        Parameters:
        db_name (string) : The name of the DB to connect to
        log_handler (logging Handler instance) : To add extra functionality to logging
        """

        client = pymongo.MongoClient(get_connect_path())
        self.db_name = db_name
        self.indexes_to_make = {}
        self.logger = logging.getLogger(__name__)
        if log_handler:
            self.logger.addHandler(log_handler)
        self.db = client[db_name]

    def index(self, table_name, index_items):
        """Creates index on the specified columns in the table of DB

        Parameters:
        table_name (string) : The Table in which the column to be indexed exists
        index_items (list) : List containing [(col_name1, type_of_index1), ...]
                             Example type_of_index is ASCENDING, DESCENDING

        Return (boolean): True if index was created, False if index creation was postponed
        """
        if table_name not in self.db.list_collection_names():
            self.logger.warning("The Collection {} does not yet exist, index "
                "will be added when the collection exists...".format(table_name))
            self.indexes_to_make[table_name] = index_items
            return False
        collection_to_index = self.db[table_name]
        conv_index = []
        for (item_name, item_type) in index_items:
            if item_type == "ASCENDING":
                conv_index.append(tuple([item_name, pymongo.ASCENDING]))
            elif item_type == "DESCENDING":
                conv_index.append(tuple([item_name, pymongo.DESCENDING]))
            else:
                self.logger.warning("Index {} not added to table {} since index "
                    "type doesn't match any pymongo indexing options".format(item_name, table_name))
        collection_to_index.create_index(conv_index)
        self.logger.debug("Index {} created for {} table".format(index_items, table_name))
        return True

    def insert(self, table_name, data):
        """Inserts data into table in DB

        Parameters:
        table_name (string) : Table in which to insert data
        data (dictionary) : Data to be inserted
        """
        if self.indexes_to_make:
            for (t_name, i_item) in self.indexes_to_make.items():
                r_val = self.index(table_name=t_name, index_items=i_item)
                if r_val == True:
                    self.indexes_to_make.pop(t_name)
        collection_to_insert = self.db[table_name]
        collection_to_insert.insert_one(data)
        self.logger.debug("Inserted data -- {} into {}".format(data, table_name))

    def find(self, table_name, query, limit_n=0, return_cols=None, return_cursor=False):
        """Search for a query in DB

        Parameters:
        table_name (string) : Name of Table to query
        query (dictionary) : Query to be carried out
        limit_n (int) : Max number of results to return in the Query
        return_cols (list) : The columns to be returned in the result, default all are returned
        return_cursor (boolean) : Returns the cursor to the DB Query

        Return (DB Cursor/List) : List if return_cursor is False, Cursor otherwise
        """
        if table_name not in self.db.list_collection_names():
            self.logger.error("The Table does not exist {} in database...".format(table_name))
            return
        collection_to_search = self.db[table_name]
        if not return_cols:
            doc_curse = collection_to_search.find(query).limit(limit_n)
        else:
            projection = {}
            for c in return_cols:
                projection[c] = 1
            doc_curse = collection_to_search.find(query, projection).limit(limit_n)
        return_obj = doc_curse
        if not return_cursor:
            return_obj = [d for d in doc_curse]
        return return_obj

    def update(self, table_name, find_q, update_q):
        """Update entries in table in DB

        Parameters:
        table_name (string) : Table to carry out updates on
        find_q (dictionary) : Query to specify items on which update has to be done
        update_q (dictionary) : {"item_to_update" : "updated_value", ...}
        """
        if table_name not in self.db.list_collection_names():
            self.logger.error("The Table does not exist {} in database...".format(table_name))
            return
        collection_to_update = self.db[table_name]
        res = collection_to_update.update_many(filter=find_q, update={"$set" : update_q})
        self.logger.debug("Successfully updated {} entries in table {} with values : {}".
                          format(res.modified_count, table_name, update_q))

    def delete_db(self):
        """Deletes the Database being handled by the API"""
        client = pymongo.MongoClient(get_connect_path())
        if self.db_name in client.list_database_names():
            self.logger.warning("Existing Database {} being deleted".format(self.db_name))
            client.drop_database(self.db_name)
        else:
            self.logger.error("Database {} does not exist ...".format(self.db_name))

    def delete_table(self, table_name):
        """Deletes a table in the database

        Parameters:
        table_name (string) : The Table to delete in Database
        """
        if table_name in self.db.list_collection_names():
            self.logger.warning("Existing Table {} being deleted from database {}".
                                format(table_name, self.db_name))
            self.db.drop_collection(table_name)
        else:
            self.logger.error("Table {} does not exist in database {}".
                              format(table_name, self.db_name))
