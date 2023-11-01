import json


class BaseExcept(Exception):
    error = None
    detail = {
        'en': 'An unknown error happened.',
        'vi': 'Có lỗi xảy ra, vui lòng thử lại sau.'
    }
    status_code = 500
    retry_after = 0

    def __init__(self, error=None, detail=None, meta=None, retry_after=0):
        if detail:
            self.detail = detail
        if retry_after:
            self.retry_after = retry_after
        if error:
            self.error = error
        else:
            self.error = self.__class__.__name__

        self.meta = meta

    def output(self):
        data = {
            'status_code': self.status_code,
            'detail': self.detail,
            'error': self.error,
        }
        if self.meta:
            data['meta'] = self.meta

        if self.retry_after:
            data['retry_after'] = self.retry_after
        return data

    def __str__(self):
        return json.dumps(self.output())


class ServiceError(BaseExcept):
    ...


class ServerError(BaseExcept):
    ...


class APIError(BaseExcept):
    ...