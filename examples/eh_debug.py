import eco_hectare as eh
import random
import datetime

# --- Sets up data base ---
db = eh.db.DataBase(db_file='../eco_hectare/static/main.db', create=True)

def insert_random_measurements(deveui, n):

    meas = [random.randint(0, 4095) for i in range(n)]
    t = datetime.datetime.today()
    ts = [(t + datetime.timedelta(seconds=60*i)).isoformat(' ', 'seconds') for i in range(n)]

    for t, m in zip(ts, meas):
        db.insert_measurement(deveui, m, t)

    
    
