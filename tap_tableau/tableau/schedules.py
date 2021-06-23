
def get_schedule_details(schedule):
    return {
        'created_at': schedule.created_at,
        'end_schedule_at': schedule.end_schedule_at,
        'execution_order': schedule.execution_order,
        'id': schedule.id,
        'interval_item': schedule.interval_item,
        'name': schedule.name,
        'next_run_at': schedule.next_run_at,
        'priority': schedule.priority,
        'schedule_type': schedule.schedule_type,
        'state': schedule.state,
        'updated_at': schedule.updated_at,
    }


def get_all_schedules(server):
    all_schedules, _ = server.schedules.get()
    return all_schedules


def get_all_schedule_details(server, authentication):
    if not server.is_signed_in():
        server.auth.sign_in(authentication)
    all_schedules = get_all_schedules(server=server)
    schedules = []
    for schedule in all_schedules:
        schedules.append(get_schedule_details(schedule=schedule))
    return schedules