from ..exception import ServiceError


class InvalidResponseType(ServiceError):
    status_code = 400


class UnAuthorized(ServiceError):
    status_code = 401


class AccessDenied(ServiceError):
    status_code = 401


class EntityNotFound(ServiceError):
    status_code = 404


class BadScoreUpdate(ServiceError):
    status_code = 400


class AccessTokenExpired(ServiceError):
    status_code = 401


class UserExisted(ServiceError):
    status_code = 409
