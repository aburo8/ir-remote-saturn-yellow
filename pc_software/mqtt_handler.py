# MQTT Handler
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QCoreApplication, QThread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from threading import Thread
class MqttHandler(Thread):
    """
    Mqtt Handler Class
    """

    def __init__(self, topic: str, hostname: str, data: str):
        super().__init__()
        self.topic = topic
        self.hostname = hostname
        self.data = data
        self.auth = {'username':"pc", 'password':"csse4011"}

    def run(self):
        """
        Put your code here that you want the thread to run
        """
        publish.single(self.topic, self.data, hostname=self.hostname, auth=self.auth)
        print("Finished Publishing!")        