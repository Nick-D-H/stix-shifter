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
        created_query_id = json.loads(create_query_response.bytes)["queryId"] if create_query_response.code == 200 else ""

        return {"code": create_query_response.code, "query_id": created_query_id}

    def get_search_status(self, search_id):
        # Check the current status of the search
        api_endpoint = "api/v2/query/{}/status".format(search_id)

        search_status_response = self.client.call_api(api_endpoint, "get")
        query_progress = json.loads(search_status_response.bytes)["progress"] if search_status_response.code == 200 else 0

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
        size = -1

        if range_end is not None:
            range_end = int(range_end)
            size = range_end
            if range_start is not None:
                range_start = int(range_start)
                size = range_end - range_start
                offset = range_start-1

        # Change API endpoint to retrieve the actual results
        search_results_response = self._get_api_results(offset, search_id, size)
        search_results_response_code = search_results_response.code
        search_results = []

        if search_results_response_code == 200:
            request_results = json.loads(search_results_response.bytes)
            # Add available result rows from the request
            search_results += request_results["rows"]
            offset += len(request_results["rows"])
            # If there are more results to retrieve repeat the process
            # Only relevant for huge result sets > 1000
            while request_results["hasMore"] and offset < size:
                # Add the number of previous results to the offset then make another call
                search_results_response = self._get_api_results(offset, search_id, size)
                request_results = json.loads(search_results_response.bytes)
                search_results += request_results["rows"]
                offset += len(request_results["rows"])
        else:
            return {"code": search_results_response_code, "message": json.loads(search_results_response.bytes)}

        return {"code": search_results_response_code, "data": search_results, "schema": search_columns}

    def _get_api_results(self, offset, search_id, size):
        api_endpoint = "api/v2/query/{}/results?offset={}&size={}".format(search_id, offset, size - offset)
        search_results_response = self.client.call_api(api_endpoint, "get")
        return search_results_response

    def delete_search(self, search_id):
        # Delete the search
        api_endpoint = "api/v2/query/{}".format(search_id)
        delete_query_response = self.client.call_api(api_endpoint, "delete")

        return {"code": delete_query_response.code, "success": True if delete_query_response.code == 200 else False}
