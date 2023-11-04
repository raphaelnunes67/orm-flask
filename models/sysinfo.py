from sql_alchemy import database
from datetime import datetime


class SysInfoModel(database.Model):
    __tablename__ = 'sysinfo'

    id = database.Column(database.Integer, primary_key=True)
    model = database.Column(database.String(80))
    quantity = database.Column(database.Integer)
    work_order = database.Column(database.String(40))
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    modified_at = database.Column(database.DateTime, default=datetime.utcnow)
    details = database.Column(database.Text)

    def __init__(self, model, quantity, work_order, details) -> None:
        self.model = model
        self.quantity = quantity
        self.work_order = work_order
        self.details = details
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()

    def json(self) -> dict:
        return {
            'id': self.id,
            'model': self.model,
            'quantity': self.quantity,
            'work_order': self.work_order,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'details': self.details
        }

    @classmethod
    def find_sysinfo(cls, id):
        sysinfo = cls.query.filter_by(id=id).first()
        if sysinfo:
            return sysinfo
        return None

    @classmethod
    def first_sysinfo(cls):
        first_id = database.session.query(cls).order_by(cls.id.asc()).first()
        if first_id is None:
            return 0
        return first_id.id

    @classmethod
    def last_sysinfo(cls) -> int:
        last_id = database.session.query(cls).order_by(cls.id.desc()).first()
        if last_id is None:
            return 0
        return last_id.id

    def save_sysinfo(self) -> None:
        database.session.add(self)
        database.session.commit()

    def update_sysinfo(self, id, model, quantity, work_order, details) -> None:
        self.id = id
        self.model = model
        self.quantity = quantity
        self.work_order = work_order
        self.modified_at = datetime.utcnow()
        self.details = details

    def delete_sysinfo(self) -> None:
        database.session.delete(self)
        database.session.commit()

    @classmethod
    def filter_results(cls, from_date_time=None, to_date_time=None, model=None):
        duts = None
        if model:
            duts = cls.query.filter(cls.model == model)
        if from_date_time:
            from_date_time = datetime.fromisoformat(from_date_time)
            if duts:
                duts = duts.filter(cls.created_at >= from_date_time)
            else:
                duts = cls.query.filter(cls.created_at >= from_date_time)
        if to_date_time:
            to_date_time = datetime.fromisoformat(to_date_time)
            if duts:
                duts = duts.filter(cls.created_at <= to_date_time)
            else:
                duts = cls.query.filter(cls.created_at <= to_date_time)
        if not duts:
            duts = cls.query.all()
        return duts

    @classmethod
    def filter_page(cls, page):
        vpp = 50
        start_id = (page * vpp) - vpp
        end_id = page * vpp
        query_value = [start_id, end_id]

        duts = cls.query.filter(cls.id >= start_id)
        duts = duts.filter(cls.id <= end_id)
        return duts

    @classmethod
    def bulk_delete(cls, ids: list) -> None:
        result = database.delete(cls).where(cls.id.in_(ids))
        database.session.execute(result)
        database.session.commit()
