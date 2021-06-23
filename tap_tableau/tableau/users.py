def get_user_details(user):
    return {
        'id': user.id,
        'auth_setting': user.auth_setting,
        'email': user.email,
        'name': user.name,
        'full_name': user.fullname,
        'role': user.site_role,
    }
