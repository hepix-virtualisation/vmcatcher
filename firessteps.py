from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper
engine = create_engine('sqlite:///tutorial.db', echo=True)
metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
    Column('password', String)
)
metadata.create_all(engine)


class Imagelist(object):
    def __init__(self, uid , fullname, password):

class Image(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)



mapper(User, users_table)
ed_user = User('ed', 'Ed Jones', 'edspassword')
print ed_user.name
