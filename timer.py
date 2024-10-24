import time

from datetime import datetime


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        # buy_time = 2020-12-22 09:59:59.500
        buy_time_everyday = '19:19:59.500'
        localtime = time.localtime(time.time())
        self.buy_time = datetime.strptime(
            localtime.tm_year.__str__() + '-' + localtime.tm_mon.__str__() + '-' + localtime.tm_mday.__str__()
            + ' ' + buy_time_everyday,
            "%Y-%m-%d %H:%M:%S.%f")
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        self.diff_time = 0


    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))


    def start(self):
        print('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time), flush=True)
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                print('时间到达，开始执行……', flush=True)
                break
            else:
                time.sleep(self.sleep_interval)