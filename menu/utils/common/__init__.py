from uuid import uuid4


def filter_empty_values(data: dict):
    return {k: v for k, v in data.items() if v}


def get_uuid4():
    return str(uuid4().hex)
