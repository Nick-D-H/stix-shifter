import json
import re

from stix_shifter_utils.stix_transmission.utils.RestApiClient import RestApiClient


class APIClient():

    def __init__(self, connection, configuration):
        # Uncomment when implementing data source API client.
        auth = configuration.get('auth')
        headers = dict()
        headers['X-Auth-Token'] = auth.get('token')
        self.client = RestApiClient(connection.get('host'),
                                    connection.get('port'),
                                    connection.get('cert', None),
                                    headers,
                                    cert_verify=connection.get('cert_verify', 'True')
                                    )

        # Placeholder client to allow dummy transmission calls.
        # Remove when implementing data source API client.
        # self.client = "data source API client"

    def ping_data_source(self):
        # Pings the data source
        # TODO: Ping the loglogic instance
        ping_response = self.client.call_api("", "get")

        return {"code": ping_response.code, "success": True if ping_response.code == 200 else False}

    def create_search(self, query_expression):
        # Queries the data source
        # TODO: Create the query in the loglogic instance using the REST API
        api_endpoint = "/api/v2/query"
        request_body = '{\
                            "query": "{}",\
                            "cached": true,\
                            "timeToLive": 0\
                        }'.format(query_expression)

        create_query_response = self.client.call_api(api_endpoint, "post", data=request_body)
        created_query_id = json.loads(create_query_response.bytes)["queryId"]

        return {"code": create_query_response.code, "query_id": created_query_id}

    def get_search_status(self, search_id):
        # Check the current status of the search
        # TODO: Check the current status of the query -> Use the "status" request
        api_endpoint = "/api/v2/query/{}/status".format(search_id)

        search_status_response = self.client.call_api(api_endpoint, "get")
        query_progress = json.loads(search_status_response.bytes)["progress"]

        return {"code": search_status_response.code, "status": "COMPLETED" if query_progress == 100 else "IN PROGRESS"}

    def get_search_results(self, search_id, range_start=None, range_end=None):
        # Return the search results. Results must be in JSON format before being translated into STIX
        # TODO: Get the results from loglogic -> Check the "hasMore" attribute and loop to get all results
        # Need to store the columns from the details endpoint As they are not included in the results
        # Then need to convert the results to JSON with their column names matched up
        # API endpoint for getting the column names
        api_endpoint = "/api/v2/query/{}/details".format(search_id)
        search_details_response = self.client.call_api(api_endpoint, "get")

        if search_details_response.code != 200:
            return {"code": search_details_response.code, "data": json.loads(search_details_response.bytes)}

        search_columns = json.loads(search_details_response.bytes)["columns"]

        # Change API endpoint to retrieve the actual results
        api_endpoint = "/api/v2/query/{}/results".format(search_id)

        search_results_response = self.client.call_api(api_endpoint, "get")
        search_results_response_code = search_results_response.code
        search_results = []

        if search_results_response_code == 200:
            request_results = json.loads(search_results_response.bytes)
            # Add available result rows from the request
            search_results.append(add_results(search_columns, request_results["rows"]))

            # If there are more results to retrieve repeat the process
            while request_results["hasMore"]:
                search_results.append(add_results(search_columns, request_results["rows"]))
        else:
            return {"code": search_results_response_code, "data": json.loads(search_results_response.bytes)}

    def delete_search(self, search_id):
        # Delete the search
        # TODO: Delete the query from loglogic
        return {"code": 200, "success": True}


def add_results(schema, results):
    # TODO: Don't add any null values & fields into the final results
    # For each row in rows
    # Add column name: value
    # Return in the format [{\"column\": value, \"column2\": value}, {\"column\": value, \"column2\": value},...]
    return_results = []

    for row in results:
        single_result = ""
        for i in range(0, len(schema)):
            # Check this comparison is correct
            if row[i] is not None:
                if row[i] is str:
                    single_result += "\"{}\": \"{}\", ".format(schema[i], row[i])
                else:
                    single_result += "\"{}\": {}, ".format(schema[i], row[i])

        # Trim the last ', '
        single_result = single_result[:len(single_result)-2]
        # Format as JSON
        single_result = "{{}}".format(single_result)
        return_results.append(single_result)

    return return_results
