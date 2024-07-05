import paho.mqtt.client as mqtt

id = "Cliente"
url = "6e487c2bb3b0422392bae2d3405c8e5f.s1.eu.hivemq.cloud"
cliente = mqtt.Client(client_id=id, clean_session=False)
cliente.connect(url, port=8883, keepalive=60)


