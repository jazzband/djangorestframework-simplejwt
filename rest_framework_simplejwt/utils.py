from calendar import timegm


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())
