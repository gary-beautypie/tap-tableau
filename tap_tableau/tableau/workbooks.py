from .connections import get_connection_details
from .permissions import get_permission_details


def get_view_details(self, view):
    return {
        'content_url': view.content_url,
        'created_at': view.created_at,
        # 'csv': view.csv,
        'id': view.id,
        # 'image': view.image,
        'name': view.name,
        'owner_id': view.owner_id,
        # 'pdf': view.pdf,
        'permissions': [get_permission_details(permission) for permission in view.permissions],
        # 'preview_image': view.preview_image,
        'project_id': view.project_id,
        'sheet_type': view.sheet_type,
        'tags': view.tags,
        # 'total_views': view.total_views,
        'updated_at': view.updated_at,
        'workbook_id': view.workbook_id
    }


def get_workbook_details(workbook):
    return {
        # 'connections': [self._get_connection_details(connection) for connection in workbook.connections],
        'content_url': workbook.content_url,
        'created_at': workbook.created_at,
        'data_acceleration_config': workbook.data_acceleration_config,
        'description': workbook.description,
        'id': workbook.id,
        'name': workbook.name,
        'owner_id': workbook.owner_id,
        'permissions': [get_permission_details(permission) for permission in workbook.permissions],
    #     'preview_image': workbook.preview_image,
        'project_id': workbook.project_id,
        'project_name': workbook.project_name,
        'show_tabs': workbook.show_tabs,
        'size': workbook.size,
        'tags': [tag for tag in workbook.tags],
        'updated_at': workbook.updated_at,
        # 'views': workbook.views,
        'webpage_url': workbook.webpage_url
    }


def get_all_workbooks(server):
    all_workbooks, _ = server.workbooks.get()
    for workbook in all_workbooks:
        server.workbooks.populate_connections(workbook)
        server.workbooks.populate_permissions(workbook)
        server.workbooks.populate_views(workbook)
    return all_workbooks


def get_all_workbook_details(server, authentication):
    workbooks = []
    connections = []
    workbook_connections = []
    if not server.is_signed_in():
        server.auth.sign_in(authentication)
    all_workbooks = get_all_workbooks(server=server)
    for workbook in all_workbooks:
        workbooks.append(get_workbook_details(workbook=workbook))
        for connection in workbook.connections:
            connections.append(get_connection_details(connection=connection))
            workbook_connections.append({'workbook_id': workbook.id, 'connection_id': connection.id})
    server.auth.sign_out()
    return {
        'workbooks': workbooks,
        'connections': connections,
        'workbook_connections': workbook_connections
    }