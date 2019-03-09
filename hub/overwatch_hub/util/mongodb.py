from pymongo.uri_parser import parse_uri


def get_mongo_db_name(uri):
    return parse_uri(uri)['database']
