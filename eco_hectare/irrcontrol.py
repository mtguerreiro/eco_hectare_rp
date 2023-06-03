import eco_hectare as eh
import numpy as np
import datetime

eh_db = eh.db.DataBase(db_file='static/main.db', create=False)

# --- Defs ---
class SectorData:
    def __init__(self, sector, cal, interval, ids):

        self.sector = sector

        self.ids = ids

        n = len(ids)
        self.ts = [None] * n
        self.val = [None] * n

        latest_data = eh_db.get_latest_measurements()

        for d in latest_data:
            i = d['deveui']
            if i in self.ids:
                idx = self.ids.index(i)
                self.ts[idx] = d['ts']
                self.val[idx] = d['value']

        self.update_all()


    def update_all(self):
        """Marks measurements older than 15 min. as invalid"""

        t = datetime.datetime.today()

        n = len(self.ids)
        for i in range(n):
            if self.ts[i] == None: continue            
            ti = datetime.datetime.strptime(self.ts[i], "%Y-%m-%d %H:%M:%S")
            dt = t - ti
            if dt.seconds > (15 * 60):
                self.ts[i] = None
                self.val[i] = None


    def update_meas(self, eui, val, ts):

        if eui in self.ids:
            idx = self.ids.index(eui)
            self.ts[idx] = ts
            self.val[idx] = val

        self.update_all()


    def mean(self):
      
        n = len(self.ids)
        acc = 0
        m = 0
        for i in range(n):
            if self.val[i] != None:
                acc = acc + self.val[i]
                m = m + 1

        if m != 0:
            avg = acc / m
        else:
            avg = None
                
        return round(avg)


    def irr_required(self):

        sector_data = eh_db.get_sector_data(self.sector)
        cal = sector_data['cal']
        interval = sector_data['interval']

        last_irrs = eh_db.get_latest_irrigations()

        if last_irrs is None:
            print('Irrigation record is empty, thus irrigation will be activated.\n')
            return True

        ts = None

        for irr in last_irrs:
            if irr['sector'] == self.sector:
                ts = irr['ts']
                break

        if ts is None:
            print('Could not find sector {:} in irrigation record. Irrigation will be activated.\n'.format(self.sector))
            return True

        t = datetime.datetime.today()
        ti = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        print('Current time: {:}'.format(t))
        print('Last irrigation: {:}'.format(ti))
        dt = t - ti
        dt = round(dt.seconds / 60 / 60)
        if dt < interval:
            return False

        print('Hora de irrigar (sector {:})'.format(self.sector))
        return True

# --- Logic ---
# Creats a list with data from all sectors
sectors = []
for sector in eh_db.get_sectors():
    devs = eh_db.get_devices_by_sector(sector['sector'])
    eui = []
    for d in devs:
        if d['type'] == 'sensor':
            eui.append(d['deveui'])

    sectors.append(
        SectorData(
            sector['sector'],
            sector['cal'],
            sector['interval'],
            eui)
        )


def proc_new_data(deveui, val, ts):

    dev_data = eh_db.get_device_data(deveui)

    if dev_data == None:
        return

    n = len(sectors)
    sector = None
    for i in range(n):
        if deveui in sectors[i].ids:
            sector = sectors[i]
            break

    if sector is None:
        return
    
    sector.update_meas(deveui, val, ts)
    avg = sector.mean()
    if avg is None:
        print('Average for sector {:} is invalid'.format(sector.sector))
        return

    eh_db.insert_avg_meas(sector.sector, avg, ts)
    
    irr_req = sector.irr_required()

