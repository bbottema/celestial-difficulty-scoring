from sqlalchemy.orm import class_mapper, selectinload


def eager_load_all_relationships(entity_type):
    mapper = class_mapper(entity_type)
    # noinspection PyTypeChecker
    relationship_attributes = [getattr(entity_type, rel.key) for rel in mapper.relationships]
    return [selectinload(attr) for attr in relationship_attributes]
