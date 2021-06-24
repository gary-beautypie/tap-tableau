import tableauserverclient as TSC

from .utils import format_datetime


def get_schedule_details(schedule):
    return {
        'created_at': format_datetime(schedule.created_at),
        'end_schedule_at': format_datetime(schedule.end_schedule_at),
        'execution_order': schedule.execution_order,
        'id': schedule.id,
        'interval_item': schedule.interval_item,
        'name': schedule.name,
        'next_run_at': format_datetime(schedule.next_run_at),
        'priority': schedule.priority,
        'schedule_type': schedule.schedule_type,
        'state': schedule.state,
        'updated_at': format_datetime(schedule.updated_at),
    }


def get_all_schedules(server_client):
    all_schedules =[]
    for schedule in TSC.Pager(server_client.schedules):
        all_schedules.append(schedule)
    return all_schedules


def get_all_schedule_details(server_client):
    all_schedules = get_all_schedules(server_client=server_client)
    schedules = []
    for schedule in all_schedules:
        schedules.append(get_schedule_details(schedule=schedule))
    return schedules
