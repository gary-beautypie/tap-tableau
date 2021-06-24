import os
import json
import logging

import singer
import singer.bookmarks as bookmarks
import singer.metrics as metrics
from singer import metadata
import tableauserverclient as TSC

from .tableau.datasources import get_all_datasource_details
from .tableau.groups import get_all_group_details
from .tableau.projects import get_all_project_details
from .tableau.schedules import get_all_schedule_details
from .tableau.tasks import get_all_task_details
from .tableau.workbooks import get_all_workbook_details


logging.disable(30) # Turn off logging from client library
logger = singer.get_logger()

REQUIRED_CONFIG_KEYS = ['host']
KEY_PROPERTIES = {
    'connections': ['id'],
    'datasources': ['id'],
    'groups': ['id'],
    'projects': ['id'],
    'schedules': ['id'],
    'tasks': ['id'],
    'users': ['id'],
    'workbooks': ['id']
}


def get_bookmark(state, stream_name, bookmark_key, start_date):
    repo_stream_dict = bookmarks.get_bookmark(state, stream_name, bookmark_key)
    if repo_stream_dict:
        return repo_stream_dict.get(bookmark_key)
    if start_date:
        return start_date
    return None


def get_all_datasources(schema, server_client, state, mdata, start_date):
    bookmark_value = get_bookmark(state, 'datasources', 'updated_at', start_date)
    if bookmark_value:
        max_record_value = singer.utils.strptime_to_utc(bookmark_value)
    else:
        max_record_value = singer.utils.strptime_to_utc("1970-01-01")
    with metrics.record_counter('datasources') as counter:
        extraction_time = singer.utils.now()
        datasource_details = get_all_datasource_details(server_client=server_client, start_date=max_record_value)
        for datasource in datasource_details['datasources']:
            with singer.Transformer() as transformer:
                rec = transformer.transform(datasource, schema, metadata=metadata.to_map(mdata))
            singer.write_record('datasources', rec, time_extracted=extraction_time)
            if singer.utils.strptime_to_utc(rec['updated_at']) > max_record_value:
                max_record_value = singer.utils.strptime_to_utc(rec['updated_at'])
            counter.increment()
            if schema.get('connections'):
                for connection in datasource_details['connections']:
                    with singer.Transformer() as transformer:
                        rec = transformer.transform(connection, schema, metadata=metadata.to_map(mdata))
                    singer.write_record('connections', rec, time_extracted=extraction_time)
    state = singer.write_bookmark(state, 'datasources', 'updated_at', singer.utils.strftime(max_record_value))
    return state


def get_all_groups(schema, server_client, state, mdata, _start_date):
    with metrics.record_counter('groups') as counter:
        extraction_time = singer.utils.now()
        group_details = get_all_group_details(server_client=server_client)
        for group in group_details['groups']:
            with singer.Transformer() as transformer:
                rec = transformer.transform(group, schema, metadata=metadata.to_map(mdata))
            singer.write_record('groups', rec, time_extracted=extraction_time)
            counter.increment()
            if schema.get('users'):
                for user in group_details['users']:
                    with singer.Transformer() as transformer:
                        rec = transformer.transform(user, schema, metadata=metadata.to_map(mdata))
                    singer.write_record('users', rec, time_extracted=extraction_time)
    return state


def get_all_projects(schema, server_client, state, mdata, _start_date):
    with metrics.record_counter('projects') as counter:
        extraction_time = singer.utils.now()
        project_details = get_all_project_details(server_client=server_client)
        for project in project_details:
            with singer.Transformer() as transformer:
                rec = transformer.transform(project, schema, metadata=metadata.to_map(mdata))
            singer.write_record('projects', rec, time_extracted=extraction_time)
            counter.increment()
    return state


def get_all_schedules(schema, server_client, state, mdata, _start_date):
    with metrics.record_counter('schedules') as counter:
        extraction_time = singer.utils.now()
        schedule_details = get_all_schedule_details(server_client=server_client)
        for schedule in schedule_details:
            with singer.Transformer() as transformer:
                rec = transformer.transform(schedule, schema, metadata=metadata.to_map(mdata))
            singer.write_record('schedules', rec, time_extracted=extraction_time)
            counter.increment()
    return state


def get_all_tasks(schema, server_client, state, mdata, _start_date):
    with metrics.record_counter('tasks') as counter:
        extraction_time = singer.utils.now()
        task_details = get_all_task_details(server_client=server_client)
        for task in task_details:
            with singer.Transformer() as transformer:
                rec = transformer.transform(task, schema, metadata=metadata.to_map(mdata))
            singer.write_record('tasks', rec, time_extracted=extraction_time)
            counter.increment()
    return state


def get_all_workbooks(schema, server_client, state, mdata, start_date):
    bookmark_value = get_bookmark(state, 'workbooks', 'updated_at', start_date)
    if bookmark_value:
        max_record_value = singer.utils.strptime_to_utc(bookmark_value)
    else:
        max_record_value = singer.utils.strptime_to_utc("1970-01-01")
    with metrics.record_counter('workbooks') as counter:
        extraction_time = singer.utils.now()
        workbook_details = get_all_workbook_details(server_client=server_client, start_date=max_record_value)
        for workbook in workbook_details['workbooks']:
            with singer.Transformer() as transformer:
                rec = transformer.transform(workbook, schema, metadata=metadata.to_map(mdata))
            singer.write_record('workbooks', rec, time_extracted=extraction_time)
            counter.increment()
        if singer.utils.strptime_to_utc(rec['updated_at']) > max_record_value:
            max_record_value = singer.utils.strptime_to_utc(rec['updated_at'])
    state = singer.write_bookmark(state, 'workbooks', 'updated_at', singer.utils.strftime(max_record_value))
    return state


SYNC_FUNCTIONS = {
    'datasources': get_all_datasources,
    'groups': get_all_groups,
    'projects': get_all_projects,
    'schedules': get_all_schedules,
    'tasks': get_all_tasks,
    'workbooks': get_all_workbooks
}

SUB_STREAMS = {
    'datasources': ['connections'],
    'groups': ['users']  ## should users be a sub-stream of groups?
}


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    schemas = {}
    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)
    return schemas


class DependencyException(Exception):
    pass


def validate_dependencies(selected_stream_ids):
    errs = []
    msg_tmpl = ("Unable to extract '{0}' data, "
                "to receive '{0}' data, you also need to select '{1}'.")

    for main_stream, sub_streams in SUB_STREAMS.items():
        if main_stream not in selected_stream_ids:
            for sub_stream in sub_streams:
                if sub_stream in selected_stream_ids:
                    errs.append(msg_tmpl.format(sub_stream, main_stream))

    if errs:
        raise DependencyException(" ".join(errs))


def populate_metadata(schema_name, schema):
    mdata = metadata.new()
    mdata = metadata.write(mdata, (), 'table-key-properties', KEY_PROPERTIES[schema_name])
    for field_name in schema['properties'].keys():
        if field_name in KEY_PROPERTIES[schema_name]:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
        else:
            mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')
    return mdata


def get_catalog():
    raw_schemas = load_schemas()
    streams = []
    for schema_name, schema in raw_schemas.items():
        mdata = populate_metadata(schema_name, schema)
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata': metadata.to_list(mdata),
            'key_properties': KEY_PROPERTIES[schema_name],
        }
        streams.append(catalog_entry)
    return {'streams': streams}


def get_selected_streams(catalog):
    '''
    Gets selected streams.  Checks schema's 'selected'
    first -- and then checks metadata, looking for an empty
    breadcrumb and mdata with a 'selected' entry
    '''
    selected_streams = []
    for stream in catalog['streams']:
        stream_metadata = stream['metadata']
        if stream['schema'].get('selected', False):
            selected_streams.append(stream['tap_stream_id'])
        else:
            for entry in stream_metadata:
                # stream metadata will have empty breadcrumb
                if not entry['breadcrumb'] and entry['metadata'].get('selected', None):
                    selected_streams.append(stream['tap_stream_id'])
    return selected_streams


def get_stream_from_catalog(stream_id, catalog):
    for stream in catalog['streams']:
        if stream['tap_stream_id'] == stream_id:
            return stream
    return None


def discover():
    catalog = get_catalog()
    print(json.dumps(catalog, indent=2))


def do_sync(config, state, catalog):
    if config.get('username') and config.get('password'):
        authentication = TSC.TableauAuth(config['username'], config['password'], site_id=config.get('site_id'))
    elif config.get('token_name') and config.get('token'):
        authentication = TSC.PersonalAccessTokenAuth(config['token_name'], config['token'], site_id=config.get('site_id'))
    else:
        raise ValueError("Must specify username/ password or token_name/ token for authentication")

    server_client = TSC.Server(config['host'], config['server_version']) if config.get('server_version') else TSC.Server(config['host'], use_server_version=True)

    if not server_client.is_signed_in():
        server_client.auth.sign_in(authentication)

    start_date = config['start_date'] if 'start_date' in config else None
    selected_stream_ids = get_selected_streams(catalog)
    validate_dependencies(selected_stream_ids)

    for stream in catalog['streams']:
        stream_id = stream['tap_stream_id']
        if not SYNC_FUNCTIONS.get(stream_id):
            continue
        if stream_id in selected_stream_ids:
            singer.write_schema(stream_id, stream['schema'], stream['key_properties'])
            sync_func = SYNC_FUNCTIONS[stream_id]
            sub_stream_ids = SUB_STREAMS.get(stream_id, None)
            if not sub_stream_ids:
                state = sync_func(stream['schema'], server_client, state, stream['metadata'], start_date)
            else:
                stream_schemas = {stream_id: stream['schema']}
                for sub_stream_id in sub_stream_ids:
                    if sub_stream_id in selected_stream_ids:
                        sub_stream = get_stream_from_catalog(sub_stream_id, catalog)
                        stream_schemas[sub_stream_id] = sub_stream['schema']
                        singer.write_schema(sub_stream_id, sub_stream['schema'], sub_stream['key_properties'])
                state = sync_func(stream_schemas, server_client, state, stream['metadata'], start_date)
            singer.write_state(state)


@singer.utils.handle_top_exception(logger)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    if args.discover:
        discover()
    else:
        catalog = args.catalog.to_dict() if args.catalog else get_catalog()
        do_sync(args.config, args.state, catalog)


if __name__ == '__main__':
    main()
