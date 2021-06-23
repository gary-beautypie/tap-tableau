from .utils import format_datetime


def get_target_details(target):
    return {
        'id': target.id,
        'type': target.type
    }


def get_task_details(task):
    return {
        'consecutive_failed_count': task.consecutive_failed_count,
        'id': task.id,
        'last_run_at': format_datetime(task.last_run_at),
        'priority': task.priority,
        'schedule_id': task.schedule_id,
        'target': get_target_details(target=task.target),
        'task_type': task.task_type
    }


def get_all_tasks(server):
    all_tasks, _ = server.tasks.get()
    return all_tasks


def get_all_task_details(server, authentication):
    if not server.is_signed_in():
        server.auth.sign_in(authentication)
    all_tasks = get_all_tasks(server=server)
    tasks = []
    for task in all_tasks:
        tasks.append(get_task_details(task=task))
    return tasks
