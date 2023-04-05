import sqlite3
import eco_hectare as eh

class DataBase:
    def __init__(self, db_file='main.db', create=False):

        self.db_file = db_file

##        self.create()
        if create == True:
            try:
                self.create()
            except:
                print('Failed to create datebase, probably exists already...\n')


    def db_connect(self, db):

        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        
        return conn

    
    def create(self):
        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Creates sectors tables
        cursor.execute("CREATE TABLE sectors(sector INTEGER PRIMARY KEY, description, cal)")

        data = [
            (0, 'null', 0),
            (1, 'batata', 0),
            (2, 'tomate', 0)
        ]

        cursor.executemany("INSERT INTO sectors VALUES(?, ?, ?)", data)
        conn.commit()

        # Creates devices table
        cursor.execute("CREATE TABLE devices(deveui PRIMARY KEY, type, sector, FOREIGN KEY(sector) REFERENCES sectors(sector))")

        data = [
            ('3dc395241c7f8501', 'atuador', 0),
            ('75775f04d7f01fe0', 'sensor', 0)
        ]

        cursor.executemany("INSERT INTO devices VALUES(?, ?, ?)", data)
        conn.commit()

        # Creates measurements table
        cursor.execute("CREATE TABLE measurements(id, deveui, value, ts, FOREIGN KEY(deveui) REFERENCES devices(deveui))")

        # Creates irrigations table
        cursor.execute("CREATE TABLE irrigations(id, sector, ts, FOREIGN KEY(sector) REFERENCES sectors(sector))")

        conn.close()


    def check_entry_exists(self, cursor, table, key, query):
        
        cmd = "SELECT count(*) FROM {:} WHERE {:} = ?".format(table, key)
        cursor.execute(cmd, (query,))

        count = cursor.fetchone()[0]

        if count == 0:
            return False
        else:
            return True


##    def add_entry(self, cursor, table, data):
##
##        cmd = "INSERT INTO {:} VALUES(?, ?, ?)"

    def delete_entry(self, cursor, table, key, row):
        
        cmd = "DELETE FROM {:} WHERE {:} = ?".format(table, key)
        cursor.execute(cmd, (row,))       

    def insert_sector(self, sector, description='', cal=0):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if sector already exists
        exists = self.check_entry_exists(cursor, 'sectors', 'sector', sector)
        if exists == True:
            print('Sector {:} is already registered!\n'.format(sector))
            return -1

        data = (sector, description, cal)
        cursor.execute("INSERT INTO sectors VALUES(?, ?, ?)", data)
        conn.commit()

        conn.close()

        return 0


    def delete_sector(self, sector):
        
        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if sector exists
        exists = self.check_entry_exists(cursor, 'sectors', 'sector', sector)
        if exists == False:
            print('Sector {:} does not exist!\n'.format(sector))
            return -1

        self.delete_entry(cursor, 'sectors', 'sector', sector)
        conn.commit()

        conn.close()
        
        return 0


    def get_sector_data(self, sector):

        conn = self.db_connect(self.db_file)

        sector_data = conn.execute('SELECT * FROM sectors WHERE sector = ?', (sector,)).fetchall()[0]

        conn.close()

        return sector_data
    

    def update_sector_data(self, sector_id, desc, cal):

        data = (desc, cal, sector_id)

        conn = self.db_connect(self.db_file)

        conn.execute('UPDATE sectors SET description = ?, cal = ? WHERE sector = ?', data)
        conn.commit()

        conn.close()
        
    def get_sectors(self):

        conn = self.db_connect(self.db_file)

        sectors = conn.execute('SELECT * FROM sectors').fetchall()

        conn.close()

        return sectors
        

        
        
        
