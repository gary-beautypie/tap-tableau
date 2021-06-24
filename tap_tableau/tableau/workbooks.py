import tableauserverclient as TSC

from .connections import get_connection_details
from .permissions import get_permission_details
from .utils import format_datetime
from .utils import get_start_date_filter


def get_view_details(view):
    return {
        'content_url': view.content_url,
        'created_at': format_datetime(view.created_at),
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
        'updated_at': format_datetime(view.updated_at),
        'workbook_id': view.workbook_id
    }


def get_workbook_details(workbook):
    return {
        # 'connections': [get_connection_details(connection) for connection in workbook.connections],
        'content_url': workbook.content_url,
        'created_at': format_datetime(workbook.created_at),
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
        'tags': list(workbook.tags),
        'updated_at': format_datetime(workbook.updated_at),
        # 'views': workbook.views,
        'webpage_url': workbook.webpage_url
    }


def get_all_workbooks(server_client, start_date):
    start_date_filter = get_start_date_filter(start_date=start_date)
    all_workbooks = []
    for workbook in TSC.Pager(server_client.workbooks, start_date_filter):
        server_client.workbooks.populate_connections(workbook)
        server_client.workbooks.populate_permissions(workbook)
        server_client.workbooks.populate_views(workbook)
        all_workbooks.append(workbook)
    return all_workbooks


def get_all_workbook_details(server_client, start_date):
    workbooks = []
    connections = []
    all_workbooks = get_all_workbooks(server_client=server_client, start_date=start_date)
    for workbook in all_workbooks:
        workbooks.append(get_workbook_details(workbook=workbook))
        for connection in workbook.connections:
            connections.append(get_connection_details(connection=connection))
    return {
        'workbooks': workbooks,
        'connections': connections,
    }
