def get_permission_details(permission):
    return {
        'capabilities': permission.capabilities,
        'grantee_id': permission.grantee.id,
        'grantee_tag_name': permission.grantee.tag_name
    }
