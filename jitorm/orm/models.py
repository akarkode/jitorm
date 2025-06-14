from .fields import Field

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {k: v for k, v in attrs.items() if isinstance(v, Field)}
        attrs['_fields'] = fields
        return super(ModelMeta, cls).__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            setattr(self, name, value)

    def save(self, session):
        session.add(self)
        session.commit()

    def __repr__(self):
        field_values = ', '.join(f"{name}={getattr(self, name)}" for name in self._fields)
        return f"<{self.__class__.__name__}({field_values})>"

    @classmethod
    def all(cls, session):
        return session.query(cls).all()

    @classmethod
    def filter(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def first(cls, session, **kwargs):
        return session.query(cls).filter_by(**kwargs).first()
