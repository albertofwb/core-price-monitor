
def get_push_date():
    from time import time, strftime, localtime
    fmt = '%Y-%m-%d %H:%M:%S'
    return strftime(fmt, localtime(time()))