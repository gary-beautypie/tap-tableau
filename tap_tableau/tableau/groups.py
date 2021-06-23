from .users import get_user_details


def get_group_details(group):
    return {
        'domain_name': group.domain_name,
        'id': group.id,
        'license_mode': group.license_mode,
        'minimum_site_role': group.minimum_site_role,
        'name': group.name,
        'tag_name': group.tag_name,
        'users': [user for user in group.users]
    }


def get_all_groups(server):
    all_groups, _ = server.groups.get()
    for group in all_groups:
        server.groups.populate_users(group)
    return all_groups


def get_all_group_details(server, authentication):
    groups = []
    users = []
    if not server.is_signed_in():
        server.auth.sign_in(authentication)
    all_groups = get_all_groups(server=server)
    for group in all_groups:
        group_details = get_group_details(group=group)
        groups.append(group_details)
        for user in group.users:
            if user.id not in set(user['id'] for user in users):
                users.append(get_user_details(user=user))
        group_details.pop('users')
    server.auth.sign_out()
    return {
        'groups': groups,
        'users': users,
    }
