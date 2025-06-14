class Field:
    def __init__(self, field_type, primary_key=False, default=None):
        self.field_type = field_type
        self.primary_key = primary_key
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, None)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

class IntegerField(Field):
    def __init__(self, primary_key=False, default=None):
        super().__init__(int, primary_key, default)

class StringField(Field):
    def __init__(self, primary_key=False, default=None):
        super().__init__(str, primary_key, default)

class BooleanField(Field):
    def __init__(self, primary_key=False, default=None):
        super().__init__(bool, primary_key, default)
