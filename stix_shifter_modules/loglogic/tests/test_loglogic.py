import unittest

from stix_shifter_modules.loglogic.entry_point import EntryPoint
from stix_shifter_utils.modules.base.stix_transmission.base_status_connector import Status

CONNECTION = {
            "host": "host",
            "port": "port",
            "path": "/"
        }
CONFIGURATION = {
            "auth": {
                "username": "placeholder username",
                "password": "placeholder password"
            }
        }
QUERY_ID = "placeholder query ID"
ENTRY_POINT = EntryPoint(CONNECTION, CONFIGURATION)


class TestLogLogicConnection(unittest.TestCase, object):
    def test_loglogic_query(self):
        query = "use Cisco_ASA, Check_Point_Interface | sys_eventTime between '2020-06-09' and '2020-06-09'"
        query_response = ENTRY_POINT.create_query_connection(query)

        assert query_response['search_id'].isdigit()

    def test_loglogic_status(self):
        status_response = ENTRY_POINT.create_status_connection(QUERY_ID)

        success = status_response["success"]
        assert success is True
        status = status_response["status"]
        assert status == Status.COMPLETED.value

    def test_loglogic_results(self):
        results_response = ENTRY_POINT.create_results_connection(QUERY_ID, 1, 10)

        success = results_response["success"]
        assert success is True
        data = results_response["data"]
        assert data == "placeholder results"

    def test_is_async(self):
        check_async = ENTRY_POINT.is_async()
        assert check_async

    def test_ping(self):
        ping_result = ENTRY_POINT.ping_connection()
        assert ping_result["success"] is True
