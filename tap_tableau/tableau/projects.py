import tableauserverclient as TSC

from .permissions import get_permission_details


def get_project_details(project):
    return {
        'content_permissions': project.content_permissions,
        'default_datasource_permissions': [get_permission_details(permission) for permission in project.default_datasource_permissions],
        'default_flow_permissions': [get_permission_details(permission) for permission in project.default_flow_permissions],
        'default_workbook_permissions': [get_permission_details(permission) for permission in project.default_workbook_permissions],
        'description': project.description,
        'id': project.id,
        'is_default': project.is_default(),
        'name': project.name,
        'owner_id': project.owner_id,
        'parent_id': project.parent_id
    }


def get_all_projects(server_client):
    all_projects = []
    for project in TSC.Pager(server_client.projects):
        server_client.projects.populate_permissions(project)
        server_client.projects.populate_datasource_default_permissions(project)
        server_client.projects.populate_flow_default_permissions(project)
        server_client.projects.populate_workbook_default_permissions(project)
        all_projects.append(project)
    return all_projects


def get_all_project_details(server_client):
    projects = []
    all_projects = get_all_projects(server_client=server_client)
    for project in all_projects:
        projects.append(get_project_details(project=project))
    return projects
