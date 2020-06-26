from stix_shifter_utils.modules.base.stix_transmission.base_results_connector import BaseResultsConnector
from stix_shifter_utils.utils.error_response import ErrorResponder


class ResultsConnector(BaseResultsConnector):
    def __init__(self, api_client):
        self.api_client = api_client

    def create_results_connection(self, search_id, offset, length):
        try:
            min_range = int(offset)
            max_range = min_range + int(length)
            # Grab the response, extract the response code, and convert it to readable json
            response_dict = self.api_client.get_search_results(search_id, min_range, max_range)
            response_code = response_dict["code"]

            # Construct a response object
            return_obj = dict()
            if response_code == 200:
                return_obj['success'] = True
                return_obj['data'] = _format_results(response_dict['schema'], response_dict['data'])
            else:
                ErrorResponder.fill_error(return_obj, response_dict, ['message'])
            return return_obj
        except Exception as err:
            print('error when getting search results: {}'.format(err))
            raise


def _format_results(schema, results):
    formatted_results = []
    formatted_results += _add_results(schema, results)

    return _json_format(formatted_results)


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
                    # To ensure JSON conformity later on, replace all " with ' in the sys_body
                    if column_name == "sys_body":
                        row[i] = row[i].replace('"', "'")

                single_result[column_name] = row[i]

        return_results.append(single_result)

    return return_results


def _json_format(search_results):
    return str(search_results).replace("{'", '{"') \
                              .replace("':", '":') \
                              .replace(": '", ': "') \
                              .replace("',", '",') \
                              .replace(", '", ', "') \
                              .replace("'},", '"},') \
                              .replace("'}]", '"}]')