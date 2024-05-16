# pub.py
import time
from umqtt.simple import MQTTClient

server="broker.emqx.io"
ClientID = f'raspberry-pub-{time.time_ns()}'
user = "emqx"
password = "public"
topic = "u47041165"
msg = """{
  "appliances": [
    {
      "name": "Living Room Light",
      "orientation": 0,
      "controls": [
        {
          "name": "Crimson Light",
          "ir_code": "#000000",
          "color": [255, 255, 0]
        },
        {
          "name": "Magenta Light",
          "ir_code": "#000001",
          "color": [255, 255, 0]
        },
        {
          "name": "Sapphire Mode",
          "ir_code": "#000002",
          "color": [255, 255, 0]
        },
        {
          "name": "Emerald Mode",
          "ir_code": "#000003",
          "color": [255, 255, 0]
        },
        {
          "name": "Golden Up",
          "ir_code": "#000004",
          "color": [255, 255, 0]
        },
        {
          "name": "Azure Down",
          "ir_code": "#000005",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Kitchen Light",
      "orientation": 1,
      "controls": [
        {
          "name": "Coral Light",
          "ir_code": "#000006",
          "color": [255, 255, 0]
        },
        {
          "name": "Lime Light",
          "ir_code": "#000007",
          "color": [255, 255, 0]
        },
        {
          "name": "Ocean Mode",
          "ir_code": "#000008",
          "color": [255, 255, 0]
        },
        {
          "name": "Ruby Mode",
          "ir_code": "#000009",
          "color": [255, 255, 0]
        },
        {
          "name": "Topaz Up",
          "ir_code": "#00000A",
          "color": [255, 255, 0]
        },
        {
          "name": "Bronze Down",
          "ir_code": "#00000B",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Bedroom Light",
      "orientation": 2,
      "controls": [
        {
          "name": "Scarlet Light",
          "ir_code": "#00000C",
          "color": [255, 255, 0]
        },
        {
          "name": "Teal Light",
          "ir_code": "#00000D",
          "color": [255, 255, 0]
        },
        {
          "name": "Indigo Mode",
          "ir_code": "#00000E",
          "color": [255, 255, 0]
        },
        {
          "name": "Amber Mode",
          "ir_code": "#00000F",
          "color": [255, 255, 0]
        },
        {
          "name": "Platinum Up",
          "ir_code": "#000010",
          "color": [255, 255, 0]
        },
        {
          "name": "Copper Down",
          "ir_code": "#000011",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Office Light",
      "orientation": 3,
      "controls": [
        {
          "name": "Vermilion Light",
          "ir_code": "#000012",
          "color": [255, 255, 0]
        },
        {
          "name": "Olive Light",
          "ir_code": "#000013",
          "color": [255, 255, 0]
        },
        {
          "name": "Cobalt Mode",
          "ir_code": "#000014",
          "color": [255, 255, 0]
        },
        {
          "name": "Pearl Mode",
          "ir_code": "#000015",
          "color": [255, 255, 0]
        },
        {
          "name": "Silver Up",
          "ir_code": "#000016",
          "color": [255, 255, 0]
        },
        {
          "name": "Brass Down",
          "ir_code": "#000017",
          "color": [255, 255, 0]
        }
      ]
    }
  ]
}"""

msg2 = """{
  "appliances": [
    {
      "name": "Living Room Light",
      "orientation": 0,
      "controls": [
        {
          "name": "Crimson Light",
          "ir_code": "#000000",
          "color": [0, 255, 255]
        },
        {
          "name": "Magenta Light",
          "ir_code": "#000001",
          "color": [0, 255, 255]
        },
        {
          "name": "Sapphire Mode",
          "ir_code": "#000002",
          "color": [0, 255, 255]
        },
        {
          "name": "Emerald Mode",
          "ir_code": "#000003",
          "color": [0, 255, 255]
        },
        {
          "name": "Golden Up",
          "ir_code": "#000004",
          "color": [0, 255, 255]
        },
        {
          "name": "Azure Down",
          "ir_code": "#000005",
          "color": [0, 255, 255]
        }
      ]
    },
    {
      "name": "Kitchen Light",
      "orientation": 1,
      "controls": [
        {
          "name": "Coral Light",
          "ir_code": "#000006",
          "color": [255, 255, 0]
        },
        {
          "name": "Lime Light",
          "ir_code": "#000007",
          "color": [255, 255, 0]
        },
        {
          "name": "Ocean Mode",
          "ir_code": "#000008",
          "color": [255, 255, 0]
        },
        {
          "name": "Ruby Mode",
          "ir_code": "#000009",
          "color": [255, 255, 0]
        },
        {
          "name": "Topaz Up",
          "ir_code": "#00000A",
          "color": [255, 255, 0]
        },
        {
          "name": "Bronze Down",
          "ir_code": "#00000B",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Bedroom Light",
      "orientation": 2,
      "controls": [
        {
          "name": "Scarlet Light",
          "ir_code": "#00000C",
          "color": [255, 255, 0]
        },
        {
          "name": "Teal Light",
          "ir_code": "#00000D",
          "color": [255, 255, 0]
        },
        {
          "name": "Indigo Mode",
          "ir_code": "#00000E",
          "color": [255, 255, 0]
        },
        {
          "name": "Amber Mode",
          "ir_code": "#00000F",
          "color": [255, 255, 0]
        },
        {
          "name": "Platinum Up",
          "ir_code": "#000010",
          "color": [255, 255, 0]
        },
        {
          "name": "Copper Down",
          "ir_code": "#000011",
          "color": [255, 255, 0]
        }
      ]
    },
    {
      "name": "Office Light",
      "orientation": 3,
      "controls": [
        {
          "name": "Vermilion Light",
          "ir_code": "#000012",
          "color": [255, 255, 0]
        },
        {
          "name": "Olive Light",
          "ir_code": "#000013",
          "color": [255, 255, 0]
        },
        {
          "name": "Cobalt Mode",
          "ir_code": "#000014",
          "color": [255, 255, 0]
        },
        {
          "name": "Pearl Mode",
          "ir_code": "#000015",
          "color": [255, 255, 0]
        },
        {
          "name": "Silver Up",
          "ir_code": "#000016",
          "color": [255, 255, 0]
        },
        {
          "name": "Brass Down",
          "ir_code": "#000017",
          "color": [255, 255, 0]
        }
      ]
    }
  ]
}"""

def connect():
    print('Connected to MQTT Broker "%s"' % (server))
    client = MQTTClient(ClientID, server, 1883, user, password)
    client.connect()
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...' % (server))
    time.sleep(5)
    client.reconnect()

try:
    client = connect()
except OSError as e:
    reconnect()

while True:
  print('send message %s on topic %s' % (msg, topic))
  client.publish(topic, msg, qos=0)
  time.sleep(8)
  client.publish(topic, msg2, qos=0)
  time.sleep(8)