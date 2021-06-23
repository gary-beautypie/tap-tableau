import argparse
import os
import json
import collections
import time

import requests
import singer
import singer.bookmarks as bookmarks
import singer.metrics as metrics
from singer import metadata
import tableauserverclient as TSC

from .tableau.datasources import get_all_datasource_details

session = requests.Session()
logger = singer.get_logger()

REQUIRED_CONFIG_KEYS = ['host']
KEY_PROPERTIES = {
    'connections': ['id'],
    'datasources': ['id']
}


def get_all_datasources(schema, server, authentication, state, mdata):
    with metrics.record_counter('datasources') as counter:
        extraction_time = singer.utils.now()
        datasource_details = get_all_datasource_details(server=server, authentication=authentication)
        for datasource in datasource_details['datasources']:
            with singer.Transformer() as transformer:
                rec = transformer.transform(datasource, schema, metadata=metadata.to_map(mdata))
            singer.write_record('datasources', rec, time_extracted=extraction_time)
            counter.increment()
            if schema.get('connections'):
                for connection in datasource_details['connections']:
                    with singer.Transformer() as transformer:
                        rec = transformer.transform(connection, schema, metadata=metadata.to_map(mdata))
                    singer.write_record('connections', rec, time_extracted=extraction_time)
    return state


SYNC_FUNCTIONS = {
    'datasources': get_all_datasources
}

SUB_STREAMS = {
    'datasources': ['connections']
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
        # get metadata for each field
        mdata = populate_metadata(schema_name, schema)
        # create and add catalog entry
        catalog_entry = {
            'stream': schema_name,
            'tap_stream_id': schema_name,
            'schema': schema,
            'metadata' : metadata.to_list(mdata),
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
                if not entry['breadcrumb'] and entry['metadata'].get('selected',None):
                    selected_streams.append(stream['tap_stream_id'])
    return selected_streams


def get_stream_from_catalog(stream_id, catalog):
    for stream in catalog['streams']:
        if stream['tap_stream_id'] == stream_id:
            return stream
    return None


def do_discover(config):
    catalog = get_catalog()
    # dump catalog
    print(json.dumps(catalog, indent=2))


def do_sync(config, state, catalog):
    if config.get('username') and config.get('password'):
        print("Using username/ password based authentication")
        authentication = TSC.TableauAuth(config['username'], config['password'], site_id=config.get('site_id'))
    elif config.get('token_name') and config.get('token'):
        print("Using token based authentication")
        authentication = TSC.PersonalAccessTokenAuth(config['token_name'], config['token'], site_id=config.get('site_id'))
    else:
        raise ValueError("Must specify username/ password or token_name/ token for authentication")
    server = TSC.Server(config['host'], use_server_version=True)

    # selected_stream_ids = get_selected_streams(catalog)
    # print(selected_stream_ids)
    for stream in catalog['streams']:
        stream_id = stream['tap_stream_id']
        stream_schema = stream['schema']
        mdata = stream['metadata']
        if not SYNC_FUNCTIONS.get(stream_id):
            continue

        singer.write_schema(stream_id, stream_schema, stream['key_properties'])
        sync_func = SYNC_FUNCTIONS[stream_id]
        sub_stream_ids = SUB_STREAMS.get(stream_id, None)
        if not sub_stream_ids:
            state = sync_func(schema=stream_schema, server=server, authentication=authentication, state=state, mdata=mdata)
        else:
            stream_schemas = {stream_id: stream_schema}

            # get and write selected sub stream schemas
            for sub_stream_id in sub_stream_ids:
                # if sub_stream_id in selected_stream_ids:
                    sub_stream = get_stream_from_catalog(sub_stream_id, catalog)
                    stream_schemas[sub_stream_id] = sub_stream['schema']
                    singer.write_schema(sub_stream_id, sub_stream['schema'], sub_stream['key_properties'])
            state = sync_func(schema=stream_schema, server=server, authentication=authentication, state=state, mdata=mdata)
        singer.write_state(state)


@singer.utils.handle_top_exception(logger)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        do_discover(args.config)
    else:
        catalog = args.properties if args.properties else get_catalog()
        do_sync(args.config, args.state, catalog)


if __name__ == '__main__':
    main()
