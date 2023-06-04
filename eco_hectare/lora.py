import json
import base64
import paho.mqtt.client as mqtt
import datetime
import zoneinfo
import eco_hectare as eh

client_address = 'localhost'

db = eh.db.DataBase(create=True)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("+/dca632fffe6bb271/#")
    #client.subscribe("+/3dc395241c7f8501/#")
    client.subscribe("application/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    deveui = base64.b64decode(data['devEUI']).hex()
    try:
        rssi = data['rxInfo'][0]['rssi']
        snr = data['rxInfo'][0]['loRaSNR']
        sensor_data = json.loads(data['objectJSON'])['dados']

        t = datetime.datetime.utcnow().astimezone(zoneinfo.ZoneInfo('America/Sao_Paulo'))
        ts = t.strftime("%Y-%m-%d %H:%M:%S")
        print('+topic: {:}\ndevEUI: {:}\tdata: {:} \ttimestamp: {:}\n\n'.format(msg.topic, deveui, sensor_data, ts))

        dev_data = db.get_device_data(deveui)
        if dev_data['type'] == 'sensor':
            db.insert_measurement(deveui, sensor_data, ts)
            db.insert_rssi_snr(deveui, rssi, snr, ts)
            eh.irrcontrol.proc_new()
    except:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(client_address, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
