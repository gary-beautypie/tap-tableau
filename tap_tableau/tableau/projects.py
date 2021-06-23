from .permissions import get_permission_details


def get_project_details(project, server, authentication):
    with server.auth.sign_in(authentication):
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


def get_all_projects(
        server,
        authentication,
        populate_permissions=True,
        populate_datasource_default_permissions=True,
        populate_flow_default_permissions=True,
        populate_workbook_default_permissions=True
):
    with server.auth.sign_in(authentication):
        all_projects, _ = server.projects.get()
        for project in all_projects:
            if populate_permissions:
                server.projects.populate_permissions(project)
            if populate_datasource_default_permissions:
                server.projects.populate_datasource_default_permissions(project)
            if populate_flow_default_permissions:
                server.projects.populate_flow_default_permissions(project)
            if populate_workbook_default_permissions:
                server.projects.populate_workbook_default_permissions(project)
    return all_projects


def get_all_project_details(server, authentication):
    projects = []
    with server.auth.sign_in(authentication):
        all_projects = get_all_projects(server=server, authentication=authentication)
        for project in all_projects:
            projects.append(get_project_details(project=project, server=server, authentication=authentication))
    return projects
