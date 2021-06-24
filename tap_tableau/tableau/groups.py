import tableauserverclient as TSC

from .users import get_user_details


def get_group_details(group):
    return {
        'domain_name': group.domain_name,
        'id': group.id,
        'license_mode': group.license_mode,
        'minimum_site_role': group.minimum_site_role,
        'name': group.name,
        'tag_name': group.tag_name,
        'users': list(group.users)
    }


def get_all_groups(server_client):
    all_groups = []
    for group in TSC.Pager(server_client.groups):
        server_client.groups.populate_users(group)
        all_groups.append(group)
    return all_groups


def get_all_group_details(server_client):
    groups = []
    users = []
    all_groups = get_all_groups(server_client=server_client)
    for group in all_groups:
        group_details = get_group_details(group=group)
        groups.append(group_details)
        for user in group.users:
            if user.id not in set(user['id'] for user in users):
                users.append(get_user_details(user=user))
        group_details.pop('users')
    return {
        'groups': groups,
        'users': users,
    }
