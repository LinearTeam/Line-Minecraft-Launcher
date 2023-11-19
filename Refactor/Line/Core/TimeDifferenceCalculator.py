import datetime

def retranslate_datetime(t):
    analysis = t.split(" ")

    ymd = analysis[0].split('-')
    year = ymd[0]
    month = ymd[1]
    day = ymd[2]

    hms = analysis[1].split(':')
    hour = hms[0]
    minute = hms[1]

    secondgroup = hms[2].split('.')
    second = secondgroup[0]
    microsecond = secondgroup[1]
    
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond))