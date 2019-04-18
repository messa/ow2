from bson import ObjectId


def to_objectid(v):
    return v if isinstance(v, ObjectId) else ObjectId(v)
