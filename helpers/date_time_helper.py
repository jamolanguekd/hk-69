import datetime

def seconds_to_dhm(seconds):
    return str(datetime.timedelta(seconds = seconds))

def get_current_timestamp():
    return datetime.utcnow()