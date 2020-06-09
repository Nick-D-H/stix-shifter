from stix_shifter_utils.utils.error_mapper_base import ErrorMapperBase
from stix_shifter_utils.utils.error_response import ErrorCode

error_mapping = {
    # Request completed successfully but no content available to return
    204: ErrorCode.TRANSMISSION_RESPONSE_EMPTY_RESULT,
    # Bad request/Invalid query
    400: ErrorCode.TRANSMISSION_QUERY_PARSING_ERROR,
    # Authentication failure, invalid access credentials
    401: ErrorCode.TRANSMISSION_AUTH_CREDENTIALS,
    # Insufficient permissions
    403: ErrorCode.TRANSMISSION_UNKNOWN,
    # Component not found
    404: ErrorCode.TRANSLATION_MODULE_DEFAULT_ERROR.value,
    # Not acceptable
    406: ErrorCode.TRANSLATION_NOTSUPPORTED,
    # Unspecified internal error
    500: ErrorCode.TRANSMISSION_CONNECT
}


class ErrorMapper():

    DEFAULT_ERROR = ErrorCode.TRANSMISSION_MODULE_DEFAULT_ERROR

    @staticmethod
    def set_error_code(json_data, return_obj):
        code = None
        try:
            code = int(json_data['code'])
        except Exception:
            pass

        error_code = ErrorMapper.DEFAULT_ERROR

        if code in error_mapping:
            error_code = error_mapping[code]

        if error_code == ErrorMapper.DEFAULT_ERROR:
            print("failed to map: " + str(json_data))

        ErrorMapperBase.set_error_code(return_obj, error_code)
