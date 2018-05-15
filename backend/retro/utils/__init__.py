
def timedelta_total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 86400) * 1000000) / 1000000


def get_store(cfg):
    pass
