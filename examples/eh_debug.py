import eco_hectare as eh
import random
import datetime
import time

# --- Sets up data base ---
db = eh.db.DataBase(db_file='../eco_hectare/static/main.db', create=True)

def insert_random_measurements(deveui, n):

    meas = [random.randint(0, 4095) for i in range(n)]
    t = datetime.datetime.today()
    ts = [(t + datetime.timedelta(seconds=60*i)).isoformat(' ', 'seconds') for i in range(n)]

    for t, m in zip(ts, meas):
        db.insert_measurement(deveui, m, t)

def getTemp():
    file = '/sys/class/hwmon/hwmon0/temp1_input'
    with open(file, 'r') as f:
        data = f.read()
    
    return float(data) / 1000.0

#insert_random_measurements('75775f04d7f01fe0', 10)
#insert_random_measurements('3dc395241c7f8501', 10)

while True:
    
    t = datetime.datetime.today().isoformat(' ', 'seconds')
    temp = getTemp()
    
    print('Temperature: {:.2f}\tTime stamp: {:}'.format(temp, t))
    db.insert_measurement('75775f04d7f01fe0', temp, t)
    
    time.sleep(60)
