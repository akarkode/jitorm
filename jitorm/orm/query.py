# from .mapping import map_to_instance
from orm.jit import LLVMJITCompiler

llvmjitcompiler = LLVMJITCompiler()

class Query:
    def __init__(self, model_class, session, fields=None):
        self.model_class = model_class
        self.session = session
        self.fields = fields if fields else f"{model_class.__name__.lower()}.*"
        self.filters = {}
        self._results = None
        self.joins = []

    def filter(self, **kwargs):
        self.filters.update(kwargs)
        return self

    def join(self, other_model_class, on_clause, fields=None):
        """ Add a join to the query with another table.
        Args:
            other_model_class: The class of the model to join.
            on_clause: The condition for the join, e.g., "User.id = Profile.user_id".
            fields: Optional fields to select from the joined table.
        """
        self.joins.append((other_model_class, on_clause, fields))
        return self

    def _get_placeholder(self):
        return "%s" if self.session.storage.database_type in ['postgresql', 'mysql'] else "?"

    def _build_query(self):
        placeholder = self._get_placeholder()
        base_query = f"SELECT {self.fields} FROM {self.model_class.__name__.lower()}"
        for model_class, on_clause, fields in self.joins:
            join_table = model_class.__name__.lower()
            join_fields = fields if fields else f"{join_table}.*"
            base_query += f" JOIN {join_table} ON {on_clause}"
            self.fields += f", {join_fields}"
        if self.filters:
            filter_clauses = []
            for key, value in self.filters.items():
                filter_clauses.append(f"{key} = {placeholder}")
            base_query += " WHERE " + " AND ".join(filter_clauses)
        return base_query, list(self.filters.values())


    def _execute_query(self, is_one:bool = False):
        query, params = self._build_query()
        self.session.storage.connect()
        cursor = self.session.storage.conn.cursor()
        try:
            cursor.execute(query, params)
            if is_one:
                row = cursor.fetchone()
                self._results = llvmjitcompiler.map(self.model_class, row) if row else None
            else:
                rows = cursor.fetchall()
                self._results = [llvmjitcompiler.map(self.model_class, row) for row in rows]
        finally:
            cursor.close()
            self.session.storage.close()
        return self._results

    def all(self):
        return self._execute_query()

    def first(self):
        return self._execute_query(is_one=True)
