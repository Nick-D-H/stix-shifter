import base64
import json

from stix_shifter_utils.stix_transmission.utils.RestApiClient import RestApiClient


class APIClient():

    def __init__(self, connection, configuration):
        # Uncomment when implementing data source API client.
        auth = configuration.get('auth')
        # Add base64 auth headers
        auth_header = "{}:{}".format(auth.get('username'), auth.get('password'))
        auth_header = base64.b64encode(bytes(auth_header, "utf-8"))
        headers = dict()
        headers['X-Auth-Token'] = auth.get('token')
        headers['Authorization'] = "Basic {}".format(str(auth_header, "utf-8"))
        self.client = RestApiClient(connection.get('host'),
                                    connection.get('port'),
                                    connection.get('cert', None),
                                    headers,
                                    cert_verify=False
                                    # connection.get('cert_verify', 'True') TODO: Reset this when finished testing
                                    )

    def ping_data_source(self):
        # Pings the data source
        ping_response = self.client.call_api("", "get")

        return {"code": ping_response.code, "success": True if ping_response.code == 200 else False}

    def create_search(self, query_expression):
        # Queries the data source
        api_endpoint = "api/v2/query"
        request_body = '{{"query": "{}", "cached": true, "timeToLive": 0}}'.format(query_expression)
        content_header = dict()
        content_header['Content-Type'] = "application/JSON"
        create_query_response = self.client.call_api(api_endpoint, "post", data=request_body, headers=content_header)
        created_query_id = json.loads(create_query_response.bytes)["queryId"]

        return {"code": create_query_response.code, "query_id": created_query_id}

    def get_search_status(self, search_id):
        # Check the current status of the search
        api_endpoint = "api/v2/query/{}/status".format(search_id)

        search_status_response = self.client.call_api(api_endpoint, "get")
        query_progress = json.loads(search_status_response.bytes)["progress"]

        return {"code": search_status_response.code, "status": "COMPLETED" if query_progress == 100 else "EXECUTE",
                "progress": query_progress}

    def get_search_results(self, search_id, range_start=None, range_end=None):
        # Return the search results. Results must be in JSON format before being translated into STIX
        # Need to store the columns from the details endpoint As they are not included in the results
        # Then need to convert the results to JSON with their column names matched up
        # API endpoint for getting the column names
        api_endpoint = "api/v2/query/{}/details".format(search_id)
        search_details_response = self.client.call_api(api_endpoint, "get")

        if search_details_response.code != 200:
            return {"code": search_details_response.code, "data": json.loads(search_details_response.bytes)}

        search_columns = json.loads(search_details_response.bytes)["columns"]

        # Results offset
        offset = 0
        # Change API endpoint to retrieve the actual results
        api_endpoint = "api/v2/query/{}/results?offset={}".format(search_id, offset)

        search_results_response = self.client.call_api(api_endpoint, "get")
        search_results_response_code = search_results_response.code
        search_results = []

        if search_results_response_code == 200:
            request_results = json.loads(search_results_response.bytes)
            # Add available result rows from the request
            search_results += _add_results(search_columns, request_results["rows"])
            # If there are more results to retrieve repeat the process
            while request_results["hasMore"]:
                # Add 100 to the offset then make another call
                offset += 100
                api_endpoint = "api/v2/query/{}/results?offset={}".format(search_id, offset)
                search_results_response = self.client.call_api(api_endpoint, "get")
                request_results = json.loads(search_results_response.bytes)
                search_results += _add_results(search_columns, request_results["rows"])
        else:
            return {"code": search_results_response_code, "message": json.loads(search_results_response.bytes)}

        # TODO: Does this need to be json.loads for the data section?
        final_results = str(search_results).replace("'", '"')
        return {"code": search_results_response_code, "data": final_results}

    def delete_search(self, search_id):
        # Delete the search
        api_endpoint = "api/v2/query/{}".format(search_id)
        delete_query_response = self.client.call_api(api_endpoint, "delete")

        return {"code": delete_query_response.code, "success": True if delete_query_response.code == 200 else False}


def _add_results(schema, results):
    # For each row in rows
    # Add column name: value
    # Return in the format [{\"column\": value, \"column2\": value}, {\"column\": value, \"column2\": value},...]
    return_results = []

    for row in results:
        single_result = {}
        for i in range(0, len(schema)):
            # Get the column name
            column_name = schema[i]["name"]
            # Strip null results
            if not isinstance(row[i], type(None)):
                if isinstance(row[i], str):
                    # Enforce string typing
                    row[i] = str(row[i])

                single_result[column_name] = row[i]

        return_results.append(single_result)

    return return_results
