# encoding:utf-8
import random

import time


def get_rand_ua():
    ua_list = [ua.replace('\n', '') for ua in open('useragents.txt', 'r').readlines()]
    return random.choice(ua_list)


def timer(func):
    def func_time():
        start = time.time()
        func()
        end = time.time()

        print '%d seconds spent！' % (int(end - start))

    return func_time
