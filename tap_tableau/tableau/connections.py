def get_connection_details(connection):
    return {
        'connection_type': connection.connection_type,
        'connection_credentials': connection.connection_credentials,
        'datasource_id': connection.datasource_id,
        'datasource_name': connection.datasource_name,
        'embed_password': connection.embed_password,
        'id': connection.id,
        'server_address': connection.server_address,
        'server_port': connection.server_port,
        'username': connection.username
    }
