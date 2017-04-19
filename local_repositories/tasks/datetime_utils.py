from datetime import datetime, timedelta

TIME_FORMAT = '%H:%M:%S'


def calculate_task_execution_timeout(task_time):
    current_datetime = datetime.now()
    current_time = get_time_from_datetime(current_datetime)
    return calculate_delta_time(task_time, current_time)


def calculate_task_next_execution_datetime(task_time):
    current_datetime = get_current_datetime()
    current_time = get_time_from_datetime(current_datetime)
    if get_time_object(current_time) >= get_time_object(task_time):
        current_datetime = add_one_day(current_datetime)
    return update_time_in_datetime(current_datetime, task_time)


def get_current_datetime():
    return datetime.now()


def calculate_delta_time(time_a_str, time_b_str):
    delta_time = (get_time_object(time_a_str) - get_time_object(time_b_str)).seconds
    if delta_time > 0:
        return delta_time
    return 60


def get_time_object(time_a):
    return datetime.strptime(time_a, TIME_FORMAT)


def get_time_from_datetime(datetime_):
    return datetime_.strftime(TIME_FORMAT)


def verify_time_format(time_str):
    try:
        datetime.strptime(time_str, TIME_FORMAT)
        return True
    except ValueError:
        return False


def update_time_in_datetime(datetime_, time_str):
    time_object = get_time_object(time_str)
    return datetime_.replace(hour=time_object.hour, minute=time_object.minute, second=time_object.second)


def add_one_day(datetime_):
    return datetime_ + timedelta(days=1)