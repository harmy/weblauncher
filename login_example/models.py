from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin
from . import app
import hashlib

db_engine = create_engine(app.config['DB_URI'])
db_session = scoped_session(sessionmaker(bind=db_engine))
db_metadata = MetaData(bind=db_engine)

Base = declarative_base()
Base.query = db_session.query_property()

class User(UserMixin, Base):
    __tablename__ = 'account'
    __table__ = Table('account', db_metadata, autoload=True)

    def is_active(self):
        return not self.forbid

    def get_id(self):
        return self.accid

    def valid_password(self, password):
        return self.password == hashlib.sha1(password).hexdigest()