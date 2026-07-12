import logging
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def success_response(data=None, message='', status=None):
    return Response(
        {'success': True, 'data': data if data is not None else {}, 'message': message},
        status=status,
    )


def error_response(message='', status=400):
    return Response({'success': False, 'error': message}, status=status)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        logger.exception('Unhandled API exception', exc_info=exc)
        return Response({'success': False, 'error': 'Internal server error'}, status=500)
    if isinstance(response.data, dict):
        detail = response.data.get('detail')
        if detail:
            response.data = {'success': False, 'error': str(detail)}
        else:
            response.data = {'success': False, 'error': response.data}
    return response
