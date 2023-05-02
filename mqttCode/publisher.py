import paho.mqtt.client as mqtt
import time


def sleep_well(duration):
    if duration <= 0.0:
        return
    begin = time.time()
    while True:
        cur = time.time()
        if cur - begin > duration:
            break
    return

class AsPublisher:


    def __init__(self, hostname="rbb041b4.ap-southeast-1.emqx.cloud", port=15197):
        self._hostname = hostname
        self._port = port
        self._current_qos = 0
        self._current_delay = 500
        self._counter = 0
        self._last_sent = time.time()
        def on_connect(client, userdata, flags, rc):
            print('connected')
            client.subscribe('request/qos')
            client.subscribe('request/delay')
            return
        def on_message(client, userdata, msg):
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            if topic == 'request/qos':
                qos = int(payload)
                if qos in {0, 1, 2}:
                    print('current qos switched to %d' % qos)
                    self._current_qos = qos
            elif topic == 'request/delay':
                delay = int(payload)
                if delay in {0, 10, 20, 50, 100, 500}:
                    print('current delay changed to %d' % delay)
                    self._current_delay = delay
            else:
                print('received message "%s": "%s"' % (topic, payload))
            return
        self._client = mqtt.Client()
        self._client.on_connect = on_connect
        self._client.on_message = on_message
        self._client.connect(self._hostname, port=self._port)
        self._client.username_pw_set("student", "33102021")
        return

    def publish_msg(self):
        qos = self._current_qos
        delay = self._current_delay
        topic = 'counter/%d/%d' % (qos, delay)
        payload = ('%d' % self._counter).encode('utf-8')
        self._counter += 1
        # publish
        self._client.publish(topic, payload=payload, qos=qos)
        print('published message "%s" : "%s"' % (topic, payload))
        # perform sleep
        sleep_well(max(0.0, self._last_sent + delay / 1000 - time.time()))
        self._last_sent = time.time()
        return
    def loop_forever(self):
        self._client.loop_start()
        while True:
            self.publish_msg()
        return
    pass
pub = AsPublisher()
pub.loop_forever()