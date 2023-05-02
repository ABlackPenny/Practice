import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import time
import matplotlib.pyplot as plt


def sleep_well(duration):
    if duration <= 0.0:
        return
    begin = time.time()
    while True:
        cur = time.time()
        if cur - begin > duration:
            break
    return
class AsAnalyser:

    def __init__(self, hostname='rbb041b4.ap-southeast-1.emqx.cloud', port=15197):
        self._hostname = hostname
        self._port = port
        self._all_qos = [0, 1, 2]
        self._all_delay = [0, 10, 20, 50, 100, 500]
        self._capturing_lock = threading.Lock()
        self._capturing_qos = None
        self._capturing_delay = None
        self._capturing_buffer = []

        def on_connect(client, userdata, flags, rc):
            print(rc)
            for qos in self._all_qos:
                for delay in self._all_delay:
                    topic = 'counter/%d/%d' % (qos, delay)
                    client.subscribe(topic, qos=qos)
            return
        def on_message(client, userdata, msg):
            _, qos, delay = msg.topic.split('/') # counter/qos/delay
            qos, delay = int(qos), int(delay)
            payload = int(msg.payload.decode('utf-8'))
            self.process_msg(qos, delay, int(payload))
            print(msg.topic," msg.payload ",msg.payload)
            return
        self._client = mqtt.Client(client_id="3310T")
        self._client.on_connect = on_connect
        self._client.on_message = on_message
        self._client.username_pw_set("student", "33102021")
        self._client.connect(self._hostname, port=self._port)
        return

    def process_msg(self, qos, delay, pid):
        self._capturing_lock.acquire()
        if qos == self._capturing_qos and delay == self._capturing_delay:
            self._capturing_buffer.append((pid, time.time()))
        self._capturing_lock.release()
        return

    def dump_csv(self, filename, x, y):
        with open(filename, 'w', encoding='utf-8') as f:
            for i in range(len(x)):
                f.write('%d,%.7f\n' % (x[i], y[i]))
        return

    def analyse(self, qos, delay, buffer, duration):
        # i. average rate
        avg_rate = len(buffer) / duration # packets / sec
        # ii. loss rate
        pids = [x[0] for x in buffer]
        expected_pkts = max(pids) - min(pids) + 1
        loss_rate = 1.0 - len(buffer) / expected_pkts
        # iii. out-of-order
        prev_pid = -1
        ooo_cnt = 0
        for pid, _ in buffer:
            if pid < prev_pid:
                ooo_cnt += 1
            prev_pid = max(prev_pid, pid)
        ooo_rate = ooo_cnt / len(buffer)
        # iv. mean, median
        gap_list = []
        for i in range(1, len(buffer)):
            if buffer[i][0] == buffer[i - 1][0] + 1:
                gap_list.append(buffer[i][1] - buffer[i - 1][1])
        gap_mean = sum(gap_list) / len(gap_list)
        gln = len(gap_list)
        s_gap_list=list(sorted(gap_list))
        gap_median=s_gap_list[gln//2]
        if gln%2==0:
            gap_median=(s_gap_list[gln//2-1]+s_gap_list[gln//2])/2
        print('i.averagerate=%.4fpackets/s'%avg_rate)
        print('ii.lossrate=%.2f%%'%(loss_rate*100))
        print('iii.ooorate=%.2f%%'%(ooo_rate*100))
        print('iv.meangap=%.2fms'%(gap_mean*1000))
        print('mediangap=%.2fms'%(gap_median*1000))
        x=list(range(0,len(gap_list)))
        y=gap_list
        self.dump_csv('anlz_q%d_d%d.csv'%(qos,delay),x,y)
        pass

    def capture(self, qos, delay):
        self._capturing_lock.acquire()
        self._capturing_qos = qos
        self._capturing_delay = delay
        # qos=self._capturing_qos
        # delay=self._capturing_delay
        self._capturing_lock.release()
        # publish.single('request/qos', payload=str(qos).encode('utf-8'), hostname=self._hostname, port=self._port,auth={'username':'student', 'password':'33102021'})
        publish.single('request/delay', payload=str(delay).encode('utf-8'), hostname=self._hostname, port=self._port,auth={'username':'student', 'password':'33102021'})
        duration =100
        sleep_well(duration)
        self._capturing_lock.acquire()
        self.analyse(qos, delay, self._capturing_buffer, duration)
        self._capturing_buffer.clear()
        self._capturing_lock.release()
        return

    def loop_forever(self):
        self._client.loop_start()
        for qos in [0]:
            for delay in [10,100,0]:
                self.capture(qos, delay)
        return

    pass

pub=AsAnalyser()
pub.loop_forever()