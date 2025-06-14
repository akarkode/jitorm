from orm.session import Session

class CRUD:
    
    @staticmethod
    def create(db: Session, model, data):
        record = model(**data)
        db.add(record)
        db.commit()
        return record
        
    @staticmethod
    def get_by_id(db: Session, model, id):
        record = db.query(model).filter(id=id).first()
        if not record:
            print(f"Data with id {id} not found.")
            return
        return record
    
    @staticmethod
    def get_list(db: Session, model):
        return db.query(model).all()
    
    @staticmethod
    def update(db: Session, model, filters, **kwargs):
        db.update(model, filters, **kwargs)
        db.commit()
        return 
    
    @staticmethod
    def delete(db: Session, model, filters):
        db.delete(model, filters)
        db.commit()
        return
    
    @staticmethod
    def bulk_create(db: Session, model, data):
        db.bulk_create(model=model, items=data)
        return
        