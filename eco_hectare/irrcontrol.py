import eco_hectare as eh
import numpy as np
import datetime
#import zoneinfo

def proc_new():
    eh_db = eh.db.DataBase()

    # --- Logic ---
    # Creats a list with data from all sectors
    sectors = {}

    latest_data = {}
    latest_irr = {}
    latest_avg = {}

    #t = datetime.datetime.today()
    t = datetime.datetime.utcnow().astimezone(zoneinfo.ZoneInfo('America/Sao_Paulo'))
    tstr = t.strftime("%Y-%m-%d %H:%M:%S")

    # Gets the latest measurement from each sensor
    for d in eh_db.get_latest_measurements():
        latest_data[d['deveui']] = {'ts':d['ts'], 'value':d['value']}

    # Gets the last irrigation time for each sector
    for d in eh_db.get_latest_irrigations():
        n = d['sector']
        latest_irr[n] = d['ts']

    # Gets the latest average for each sector
    for d in eh_db.get_latest_average():
        n = d['sector']
        latest_avg[n] = {'ts':d['ts'], 'value':d['value']}
        
    # Fills in essential sector data
    for sector in eh_db.get_sectors():
        n = sector['sector']
        sectors[n] = {'ts':[], 'value':[], 'atuador':[], 'irr': False}
        sec_data = eh_db.get_sector_data(n)
        sectors[n]['cal'] = sec_data['cal']
        sectors[n]['interval'] = sec_data['interval']
        devs = eh_db.get_devices_by_sector(n)
        for d in devs:
            if d['type'] == 'sensor' and d['deveui'] in latest_data:
                ts = latest_data[d['deveui']]['ts']
                value = latest_data[d['deveui']]['value']
                tm = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                dt = t - tm
                if dt.seconds < (15 * 60):
                    # Only adds measurements if they are recent enough
                    sectors[n]['ts'].append(ts)
                    sectors[n]['value'].append(value)
            elif d['type'] == 'atuador':
                sectors[n]['atuador'].append(d['deveui'])
                    
        if n in latest_irr:
            tm = datetime.datetime.strptime(latest_irr[n], "%Y-%m-%d %H:%M:%S")
            dt = t - tm
            sectors[n]['last_irr'] = latest_irr[n]
            sectors[n]['last_irr_dt'] = dt.seconds
        else:
            sectors[n]['last_irr'] = None
            sectors[n]['last_irr_dt'] = None

    # Computes the average with the latest measurements
    for sec_n, sec_data in sectors.items():
        n = len(sec_data['value'])
        acc = sum(sec_data['value'])
        if n != 0: sec_avg = round(acc / n)
        else: sec_avg = None
        sec_data['avg'] = sec_avg

        # Checks if latest average is already stored
        if sec_avg is not None:
            last = sorted(sec_data['ts'],
                          key = lambda d: datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                          reverse=True)[0]

            if (latest_avg == {}) or (last != latest_avg[sec_n]['ts']):
                eh_db.insert_avg_meas(sec_n, sec_avg, last)

    # Determines whether irrigation is required
    for sec_n, sec_data in sectors.items():
        print(sec_data)
        cal = sec_data['cal']
        avg = sec_data['avg']
        sec_data['irr'] = False
        if avg is None:
            sec_data['irr'] = False
        else:        
            if avg < cal:
                if sec_data['last_irr'] is None:
                    sec_data['irr'] = True
                else:
                    dt = sec_data['last_irr_dt'] / 60 / 60
                    if dt > sec_data['interval']:
                        sec_data['irr'] = True

        # Send downlinks as necessary
        if sec_data['irr'] is True:
            for actuator in sec_data['atuador']:
                eh.downlink.send_downlink(actuator)
            eh_db.insert_irrigation(sec_n, tstr)
    
    print('|{:^7}|{:^7}|{:^7}|{:^11}|{:^30}|{:^10}'.format('Setor', 'Cal', 'Media', 'Intervalo', 'Ultima irr. (dt)', 'Irrig?'))
    for sec_n, sector in sectors.items():
        
        cal = sector['cal']
        
        avg = sector['avg']
        
        if avg is None: avg = '--'
        
        interval = sector['interval']

        last_irr = sector['last_irr']
        if last_irr is None: last_irr = '--'
        
        last_irr_dt = sector['last_irr_dt']
        if last_irr_dt is None: last_irr_dt = '--'
        else:
            minutes = int(last_irr_dt / 60)
            h = int(minutes / 60 )
            mints = minutes % 60
            last_irr_dt = '{:02}:{:02}'.format(h, mints)

        irrig = sector['irr']
        if irrig is False: irrig = 'Nao'
        else: irrig = 'Sim'
        
        print('|{:^7}|{:^7}|{:^7}|{:^11}|{:^21} ({:^5}) |{:^10}'.format(sec_n, cal, avg, interval, last_irr, last_irr_dt, irrig))
