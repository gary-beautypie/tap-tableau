import tableauserverclient as TSC

from .connections import get_connection_details
from .permissions import get_permission_details
from .utils import format_datetime
from .utils import get_start_date_filter


def get_datasource_details(datasource):
    return {
        'ask_data_enablement': datasource.ask_data_enablement,
        'certification_note': datasource.certification_note,
        'certified': datasource.certified,
        'content_url': datasource.content_url,
        'created_at': format_datetime(datasource.created_at),
        'datasource_type': datasource.datasource_type,
        'description': datasource.description,
        'encrypt_extracts': datasource.encrypt_extracts,
        'has_extracts': datasource.has_extracts,
        'id': datasource.id,
        'name': datasource.name,
        'owner_id': datasource.owner_id,
        'permissions': [get_permission_details(permission) for permission in datasource.permissions],
        'project_id': datasource.project_id,
        'project_name': datasource.project_name,
        'tags': list(datasource.tags),
        'updated_at': format_datetime(datasource.updated_at),
        'use_remote_query_agent': datasource.use_remote_query_agent,
        'webpage_url': datasource.webpage_url
    }


def get_all_datasources(server_client, start_date):
    start_date_filter = get_start_date_filter(start_date=start_date)
    all_datasources = []
    for datasource in TSC.Pager(server_client.datasources, start_date_filter):
        server_client.datasources.populate_connections(datasource)
        server_client.datasources.populate_permissions(datasource)
        all_datasources.append(datasource)
    return all_datasources


def get_all_datasource_details(server_client, start_date):
    connections = []
    datasources = []
    all_datasources = get_all_datasources(server_client=server_client, start_date=start_date)
    for datasource in all_datasources:
        datasources.append(get_datasource_details(datasource=datasource))
        for connection in datasource.connections:
            connections.append(get_connection_details(connection=connection))
    return {
        'datasources': datasources,
        'connections': connections,
    }
