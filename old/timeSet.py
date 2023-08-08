import datetime

from dateutil import relativedelta


# export time set
# before_month = REQUIRED, set base export month(0 = now month, 1 = prev month, 2 = -2 month ...)
# range_month = REQUIRED, set export range (1 = befare_month-1, 5 = before_month-5 ...)
# log_group_name = REQUIRED, set export log group name, it replace '/' to '-'
# destination prefix = OPTION, set bucket prefix
# timezone = OPTION, insert your timezone
def timeSet(before_month, range_month, log_group_name, destination_prefix, timezone):
    nowTime = datetime.datetime.utcnow()

    this_month = datetime.datetime(
        year=nowTime.year, month=nowTime.month, day=1, hour=0, minute=0, second=0) - relativedelta.relativedelta(months=before_month)
    prev_month = this_month - relativedelta.relativedelta(months=range_month)
    first_day = prev_month - datetime.timedelta(hours=timezone)
    last_day = this_month - \
        datetime.timedelta(seconds=1) - datetime.timedelta(hours=timezone)
    destination_prefix_val = destination_prefix+'/'+str(
        last_day.year)+'/'+str(last_day.month).zfill(2)+'/'+log_group_name.replace('/', '-')

    return {
        'this_month': this_month,
        'prev_month': prev_month,
        'first_day': first_day,
        'last_day': last_day,
        'destination_prefix_val': destination_prefix_val
    }


timeSet(0, 1, 'test/test123', 'prefixtest', 9)
