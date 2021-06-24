# tap-tableau

This is a [Singer](https://singer.io) tap that produces JSON-formatted data from the [Tableau REST API](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm) following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).  
Although it currently relies on this API, the intention will be to move over to the [Metadata API](https://help.tableau.com/current/api/metadata_api/en-us/index.html).  

| Stream | Replication Key | Replication Strategy |
|:---:|:---:|:---:|
| Connections | id | FULL |
| Datasources | id | INCREMENTAL |
| Groups | id | FULL |
| Permissions | id | FULL |
| Projects | id | FULL |
| Schedules | id | FULL |
| Tasks | id | FULL |
| Users | id | FULL |
| Workbooks | id | INCREMENTAL |


## Quick start

1. Install

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > pip install tap-tableau
    ```

2. Create the config file, either (`token`, `token_name`) or (`username`, `password`) must
 be specified for authentication.

    ```json
    {
       "token_name": "My Tableau API access token",
       "token": "abcdefg12345==",
       "site_id": "my_tableau_site",
       "host": "https://my_tableau_site.com",
       "start_date": "2021-01-01T00:00:00Z"
   }
    ```

3. Run discovery to generate the catalog

    ```bash
    tap-tableau --config config.json --discover > catalog.json
    ```

4. In the catalog.json file, select the streams to sync

    Each stream in the catalog.json file has a "schema" entry.  To select a stream to sync, add `"selected": true` to that stream's "schema" entry.  For example, to sync the datasources stream:
    ```
    ...
    "tap_stream_id": "datasources",
    "schema": {
      "selected": true,
      "schema": {
        "updated_at": {
          "format": "date-time",
          "type": [
            "null",
            "string"
          ]
        }
    ...
    ```

5. Run the application

    `tap-tableau` can be run with:

    ```bash
    tap-tableau --config config.json --catalog catalog.json
    ```
    To include a state file:
    ```bash
    tap-tableau --config config.json --catalog catalog.json > state.json
    tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
