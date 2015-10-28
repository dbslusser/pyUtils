#! /usr/bin/python
"""
Description:
    Collection of utilities to facilitate database interactions.
"""
import MySQLdb
import logging


class dbase:
    """
    Description:
        A collection of methods to control mySQL database transactions.

    Parameters:
        db_name - name of database
        host    - host (name or IP address) of database server
        user    - user ID 
        passwd  - user password
    """
    
    def __init__(self, db_name, host, user, passwd):
        """ Class entry point"""
        self.db_host = host
        self.db_user = user
        self.db_passwd = passwd
        self.db_name = db_name
        self.connect()

    def connect(self):
        """ 
        Description:
            Establish db connection
        """
        self.db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_passwd, db=self.db_name)
        self.cursor = self.db.cursor()

    def close(self):
        """
        Description:
            Close db connection
        """
        self.cursor.close()
        self.db.close()

    def getDbServerOs(self):
        """
        Description:
            Returns the operating system and version on which the database resides.

        Returns:
            string describing OS and version
        """
        self.cursor.execute("SELECT VERSION()")
        return self.cursor.fetchone()[0]

    def getDataBases(self, db_type=None):
        """
        Description:
            Returns a list of databases available on the server.

        Parameters:
            db_type - type of database (such as projects)

        Returns:
            list of database names
        """
        self.cursor.execute("show databases")
        return [db[0] for db in self.cursor.fetchall()]

    def getTables(self):
        """
        Description:
            Returns a list containing names of all tables in the database.
        """
        self.cursor.execute("show tables")
        return [row[0] for row in self.cursor]

    def getColumnNames(self, table):
        """
        Description:
            Returns a list of field (column) names for a given table.

        Paramters:
            table   name of table

        Returns:
            list of field names in table
        """
        self.cursor.execute("DESCRIBE %s" % table)
        return [row[0] for row in self.cursor]

    def getColumnCount(self, table):
        """
        Description:
            Returns the field (column) count for a given table.

        Parameters:
            table - name of table

        Returns:
            number of fields in table
        """
        self.cursor.execute("select * from %s" % table)
        return self.db.field_count()

    def getRowCount(self, table):
        """
        Description:
            Returns the record (row) count for a given table.

        Parameters:
            table - name of table

        Returns:
            number of records in table
        """        
        self.cursor.execute("SELECT COUNT(*) FROM %s" % table)
        return self.cursor.fetchall()[0][0]

    def getAllRows(self, table):
        """
        Description:
            Retrieves all data (rows and fields) from a given table.

        Parametes:
            table - name of table to retrieve data from

        Returns:
            tuple of tuples (row data)
        """
        self.cursor.execute("select * from %s" % table)
        return self.cursor.fetchall()

    def insertRow(self, table, d, debug=0):
        """
        Description:
            Inserts a record to the table
        
        Parameters:
            table - name of table to add record to
            d     - dictionary containing column name (key) and value (value)
        
        Returns:
            id of new row
        """
        ## check keys against column names
        valid_columns = self.getColumnNames(table)
        for k in d.keys():
            if k not in valid_columns:
                d.pop(k)

        new_row = -1
        field_list = []
        value_list = []
        for k,v in d.iteritems():
            field_list.append(k)
            value_list.append(v)
        fields = ', '.join(['`%s`' % i for i in field_list])
        values = ', '.join(['%s' % i if type(i).__name__ in ['int', 'long'] else '"%s"' % i for i in value_list])
        cmd = '''INSERT INTO `%s` (%s) VALUES (%s)''' % (table,fields,values)
        print cmd
        logging.debug(cmd)
        try:
            self.cursor.execute(cmd)
            self.db.commit()
            new_row = max([i[0] for i in self.selectRow(table, where_data=d)])
        except MySQLdb.Error, e:
            logging.debug("%s: %s", e[0], e[1])
            return -1
        return new_row
      
    def updateRow(self, table, set_data, where_data, debug=0):
        """
        Description:
            Updates a record to the table
        
        Parameters:
            table      - name of table to containing record to update
            set_data   - dictionary containing column name (key) and value (value) of data to update
            where_data - dictionary containing column name (key) and value (value) of data to match
        """
        cmd = 'UPDATE %s SET ' % table
        cmd += ', '.join(['%s=%s' % (k,v) if type(v).__name__ == 'int' else '%s="%s"' % (k,v) for k,v in set_data.iteritems()])
        compound = False
        cmd += ' WHERE'
        for k,v in where_data.iteritems():
            if compound: cmd += ''' AND'''
            else: compound = True
            if type(v).__name__ == 'int':
                cmd += ''' %s=%s''' % (k,v)
            else:
                cmd += ''' %s="%s"''' % (k,v)
        logging.debug(cmd)
        self.cursor.execute(cmd)
        self.db.commit()

    def deleteRow(self, table, d=None, debug=0):
        """
        Description:
            Removes a record from the table
        
        Parameters:
            table - name of table
            d     - dictionary containing column name (key) and value (value)
        """
        if not d:
            cmd = '''DELETE FROM %s''' % table
        else:
            cmd = '''DELETE FROM %s WHERE''' % table
            compound = False
            for k,v in d.iteritems():
                if compound: cmd += ''' AND'''
                else: compound = True
                if type(v).__name__ == 'int':
                    cmd += ''' %s=%s''' % (k,v)
                else:
                    cmd += ''' %s="%s"''' % (k,v)
        logging.debug(cmd)
        self.cursor.execute(cmd)

    def selectRow(self, table, cols=None, where_data=None, debug=0, dict=False):
        """
        Description:
            Retrieves records from a table
        
        Parameters:
            table      - name of table to get data from
            cols       - names of column(s) to get data from; defaults to all
            where_data - dictionary containing column name (key) and value (value) of data to match
        
        Returns:
            records matching search criteria (tuple of tuples)
        """
        cmd = 'SELECT'
        if cols: cmd += ' %s' % cols
        else: cmd += ' *'
        cmd += ' FROM %s' % table
        if where_data:
            cmd += ' WHERE'
            compound = False
            for k,v in where_data.iteritems():
                if compound: cmd += ''' AND'''
                else: compound = True
                if type(v).__name__ == 'int':
                    cmd += ''' `%s`=%s''' % (k,v)
                else:
                    cmd += ''' `%s`="%s"''' % (k,v)
        if debug:
            logging.debug(cmd)
        self.cursor.execute(cmd)
        resp = self.cursor.fetchall()
        if dict:
            return self.resultsToDict(table, resp)
        return resp

    def runSql(self, query, debug=0, flat=False):
        """
        Description:
            Execute a custom SQL command
        
        Parameters:
            query - sql query to run
        
        Returns:
            result of query (tuple of tuples)
        """
        logging.debug(query)
        self.cursor.execute(query)
        if flat:
            return self.flattenResults(self.cursor.fetchall())
        return self.cursor.fetchall()
        
    def resultsToDict(self, table, results):
        """
        Takes a tuple of tuple database query results and builds a python dictionary
        """
        records = []
        column_names = self.getColumnNames(table)
        for row in results:
            row_index = 0
            d = {}
            for col in row:
                d[column_names[row_index]] = col
                row_index += 1
            records.append(d)
        return records

    def flattenResults(self, results):
        """
        Description:
            flattens a tuple of results into a single list
        
        Parameters:
            results - tuple of tuples
        
        Returns:
            list of results
         """
        if results:
            return reduce(list.__add__, (list(i) for i in results))




