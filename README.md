# tap-tableau

This is a [Singer](https://singer.io) tap that produces JSON-formatted data from the Tableau REST API following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).  


## Quick start

1. Install

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > pip install tap-tableau
    ```

2. Create the config file 

    ```json
    {
       "token_name": "My Tableau API access token",
       "token": "abcdefg12345==",
       "site_id": "my_tableau_site",
       "host": "https://my_tableau_site.com",
       "start_date": "2021-01-01T00:00:00Z"
   }
    ```

3. Run the tap in discovery mode to get properties.json file

    ```bash
    tap-tableau --config config.json --discover > catalog.json
    ```

4. In the catalog.json file, select the streams to sync

    Each stream in the properties.json file has a "schema" entry.  To select a stream to sync, add `"selected": true` to that stream's "schema" entry.  For example, to sync the pull_requests stream:
    ```
    ...
    "tap_stream_id": "datasources",
    "schema": {
      "selected": true,
      "properties": {
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
