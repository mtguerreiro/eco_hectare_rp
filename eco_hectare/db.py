import sqlite3
import eco_hectare as eh

class DataBase:
    def __init__(self, db_file='static/main.db', create=False):

        self.db_file = db_file

        if create == True:
            try:
                self.create()
            except:
                print('Failed to create database, probably exists already...\n')


    def db_connect(self, db):

        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        
        return conn

    
    def create(self):
        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Creates sectors tables
        cursor.execute("CREATE TABLE sectors(sector INTEGER PRIMARY KEY, description, cal, interval)")

        # Creates devices table
        cursor.execute("CREATE TABLE devices(deveui PRIMARY KEY, type, sector, FOREIGN KEY(sector) REFERENCES sectors(sector))")

        # Creates measurements table
        cursor.execute("CREATE TABLE measurements(id INTEGER PRIMARY KEY, deveui, value INTEGER, ts, FOREIGN KEY(deveui) REFERENCES devices(deveui))")

        # Creates sector average measurements table
        cursor.execute("CREATE TABLE sector_avg_meas(id INTEGER PRIMARY KEY, sector, value INTEGER, ts, FOREIGN KEY(sector) REFERENCES sectors(sector))")
        
        # Creates RSSI and SNR tables
        cursor.execute("CREATE TABLE rssi_snr(id INTEGER PRIMARY KEY, deveui, rssi, snr, ts, FOREIGN KEY(deveui) REFERENCES devices(deveui))")
        
        # Creates irrigations table
        cursor.execute("CREATE TABLE irrigations(id INTEGER PRIMARY KEY, sector, ts, FOREIGN KEY(sector) REFERENCES sectors(sector))")

        conn.close()


    def check_entry_exists(self, cursor, table, key, query):
        
        cmd = "SELECT count(*) FROM {:} WHERE {:} = ?".format(table, key)
        cursor.execute(cmd, (query,))

        count = cursor.fetchone()[0]

        if count == 0:
            return False
        else:
            return True


    def delete_entry(self, cursor, table, key, row):
        
        cmd = "DELETE FROM {:} WHERE {:} = ?".format(table, key)
        cursor.execute(cmd, (row,))       


    def insert_sector(self, sector, description='', cal=0, interval=0):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if sector already exists
        exists = self.check_entry_exists(cursor, 'sectors', 'sector', sector)
        if exists == True:
            print('Sector {:} is already registered!\n'.format(sector))
            return -1

        data = (sector, description, cal, interval)
        cursor.execute("INSERT INTO sectors VALUES(?, ?, ?, ?)", data)
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
    

    def update_sector_data(self, sector_id, desc, cal, interval):

        data = (desc, cal, interval, sector_id)

        conn = self.db_connect(self.db_file)

        conn.execute('UPDATE sectors SET description = ?, cal = ?, interval = ? WHERE sector = ?', data)
        conn.commit()

        conn.close()

    
    def get_sectors(self):

        conn = self.db_connect(self.db_file)

        sectors = conn.execute('SELECT * FROM sectors').fetchall()

        conn.close()

        return sectors

    
    def get_devices_by_sector(self, sector):

        conn = self.db_connect(self.db_file)
        
        devices = conn.execute('SELECT * FROM devices WHERE sector = ?', (sector,)).fetchall()

        conn.close()

        return devices


    def get_devices(self):

        conn = self.db_connect(self.db_file)

        devices = conn.execute('SELECT * FROM devices').fetchall()

        conn.close()

        return devices


    def get_device_data(self, deveui):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if device exists
        exists = self.check_entry_exists(cursor, 'devices', 'deveui', deveui)
        if exists == False:
            print('deveui {:} does not exist!\n'.format(deveui))
            return None
        
        device_data = conn.execute('SELECT * FROM devices WHERE deveui = ?', (deveui,)).fetchall()[0]

        conn.close()

        return device_data


    def insert_device(self, deveui, sector=0, dev_type='sensor'):

        if dev_type != 'sensor' and dev_type != 'atuador':
            print('Device type must be \'sensor\' or \'atuador\'')
            return -1

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if device already exists
        exists = self.check_entry_exists(cursor, 'devices', 'deveui', deveui)
        if exists == True:
            print('deveui {:} is already registered!\n'.format(deveui))
            return -2

        data = (deveui, dev_type, sector)
        cursor.execute("INSERT INTO devices VALUES(?, ?, ?)", data)
        conn.commit()

        conn.close()       

        return 0


    def delete_device(self, deveui):
        
        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if device exists
        exists = self.check_entry_exists(cursor, 'devices', 'deveui', deveui)
        if exists == False:
            print('deveui {:} does not exist!\n'.format(deveui))
            return -1

        self.delete_entry(cursor, 'devices', 'deveui', deveui)
        conn.commit()

        conn.close()
        
        return 0


    def update_device_data(self, deveui, sector=0, dev_type='sensor'):

        if dev_type != 'sensor' and dev_type != 'atuador':
            print('Device type must be \'sensor\' or \'atuador\'')
            return -1

        data = (sector, dev_type, deveui)

        conn = self.db_connect(self.db_file)

        conn.execute('UPDATE devices SET sector = ?, type = ? WHERE deveui = ?', data)
        conn.commit()

        conn.close()

        return 0

    
    def insert_measurement(self, deveui, value, ts):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if device exists
        exists = self.check_entry_exists(cursor, 'devices', 'deveui', deveui)
        if exists == False:
            print('deveui {:} does not exist!\n'.format(deveui))
            return -1

        data = (deveui, value, ts)
        cursor.execute("INSERT INTO measurements (deveui, value, ts) VALUES(?, ?, ?)", data)
        conn.commit()

        conn.close()

        return 0


    def get_latest_measurements(self):

        conn = self.db_connect(self.db_file)
    
        cursor = conn.cursor()
        
        res = cursor.execute("SELECT t1.* FROM measurements AS t1 LEFT OUTER JOIN measurements AS t2 ON t1.deveui = t2.deveui AND (t1.ts < t2.ts OR (t1.ts = t2.ts AND t1.id < t2.id)) WHERE t2.deveui IS NULL").fetchall()
        #res = cursor.execute("SELECT t1.* FROM measurements t1 WHERE t1.id = (SELECT t2.id FROM measurements t2 WHERE t2.deveui = t1.deveui ORDER BY t2.ts DESC LIMIT 1)").fetchall()

        conn.close()
        
        return res

    
    def insert_rssi_snr(self, deveui, rssi, snr, ts):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if device exists
        exists = self.check_entry_exists(cursor, 'devices', 'deveui', deveui)
        if exists == False:
            print('deveui {:} does not exist!\n'.format(deveui))
            return -1

        data = (deveui, rssi, snr, ts)
        cursor.execute("INSERT INTO rssi_snr (deveui, rssi, snr, ts) VALUES(?, ?, ?, ?)", data)
        conn.commit()

        conn.close()

        return 0


    def insert_irrigation(self, sector, ts):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if sector exists
        exists = self.check_entry_exists(cursor, 'sectors', 'sector', sector)
        if exists == False:
            print('Sector {:} does not exist!\n'.format(sector))
            return -1

        data = (sector, ts)
        cursor.execute("INSERT INTO irrigations (sector, ts) VALUES(?, ?)", data)
        conn.commit()

        conn.close()

        return 0


    def get_latest_irrigations(self):

        conn = self.db_connect(self.db_file)
    
        cursor = conn.cursor()
        
        res = cursor.execute("SELECT t1.* FROM irrigations AS t1 LEFT OUTER JOIN irrigations AS t2 ON t1.sector = t2.sector AND (t1.ts < t2.ts OR (t1.ts = t2.ts AND t1.id < t2.id)) WHERE t2.sector IS NULL").fetchall()
        #res = cursor.execute("SELECT t1.* FROM measurements t1 WHERE t1.id = (SELECT t2.id FROM measurements t2 WHERE t2.deveui = t1.deveui ORDER BY t2.ts DESC LIMIT 1)").fetchall()

        conn.close()
        
        return res


    def insert_avg_meas(self, sector, value, ts):

        conn = self.db_connect(self.db_file)

        cursor = conn.cursor()

        # Check if sector exists
        exists = self.check_entry_exists(cursor, 'sectors', 'sector', sector)
        if exists == False:
            print('Sector {:} does not exist!\n'.format(sector))
            return -1

        data = (sector, value, ts)
        cursor.execute("INSERT INTO sector_avg_meas (sector, value, ts) VALUES(?, ?, ?)", data)
        conn.commit()

        conn.close()

        return 0
