from .query import Query

class Session:
    def __init__(self, storage):
        self.storage = storage
        self._transaction = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def _get_placeholder(self):
        return "%s" if self.storage.database_type in ['postgresql', 'mysql'] else "?"

    def add(self, model):
        placeholders = self._get_placeholder()
        fields = ', '.join([f for f in model._fields if getattr(model, f) is not None])
        values = tuple(getattr(model, f) for f in model._fields if getattr(model, f) is not None)
        placeholder_string = ', '.join([placeholders for _ in values])
        query = f"INSERT INTO {model.__class__.__name__.lower()} ({fields}) VALUES ({placeholder_string})"
        last_row_id = self.storage.execute(query, values)
        pk_field = next((f for f in model._fields if getattr(model._fields[f], 'primary_key', False)), None)
        if not pk_field:
            raise ValueError("No primary key defined for the model.")
        setattr(model, pk_field, last_row_id)
        return model

    def commit(self):
        self.storage.commit()
        self._transaction.clear()

    def rollback(self):
        self._transaction.clear()

    def query(self, model_class, fields=None):
        return Query(session=self, model_class=model_class, fields=fields)

    def bulk_create(self, model, items, batch_size=1000):
        placeholders = self._get_placeholder()
        columns = ', '.join(items[0].keys())
        placeholder_string = f"({', '.join([placeholders] * len(items[0]))})"
        query = f"INSERT INTO {model.__name__.lower()} ({columns}) VALUES "

        cursor = None
        try:
            cursor = self.storage.conn.cursor()
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                params = []
                value_strings = []

                for item in batch:
                    params.extend(tuple(item.values()))
                    value_strings.append(placeholder_string)

                # Gabungkan query final dengan batch values
                final_query = query + ', '.join(value_strings)
                try:
                    cursor.execute(final_query, params)
                except Exception as e:
                    print(f"Error executing query: {e}")
                    raise
        finally:
            if cursor:
                cursor.close()

        self.commit()

    def update(self, model_class, filters, **kwargs):
        placeholders = self._get_placeholder()
        set_clause = ', '.join([f"{key} = {placeholders}" for key in kwargs])
        filter_clause = ' AND '.join([f"{key} = {placeholders}" for key in filters])
        query = f"UPDATE {model_class.__name__.lower()} SET {set_clause} WHERE {filter_clause}"
        params = list(kwargs.values()) + list(filters.values())
        self.storage.execute(query, params)
        self.storage.commit()

    def delete(self, model_class, filters):
        placeholders = self._get_placeholder()
        filter_clauses = ' AND '.join([f"{key} = {placeholders}" for key in filters])
        params = list(filters.values())
        query = f"DELETE FROM {model_class.__name__.lower()} WHERE {filter_clauses}"
        self.storage.execute(query, params)
        self.storage.commit()
