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
        return {"code": 200, "query_id": "uuid_1234567890"}

    def get_search_status(self, search_id):
        # Check the current status of the search
        # TODO: Check the current status of the query -> Use the "status" request
        return {"code": 200, "status": "COMPLETED"}

    def get_search_results(self, search_id, range_start=None, range_end=None):
        # Return the search results. Results must be in JSON format before being translated into STIX
        # TODO: Get the results from loglogic -> Check the "hasMore" attribute and loop to get all results
        return {"code": 200, "data": "Results from search"}

    def delete_search(self, search_id):
        # Optional since this may not be supported by the data source API
        # Delete the search
        # TODO: Delete the query from loglogic
        return {"code": 200, "success": True}
