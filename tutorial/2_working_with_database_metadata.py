from sqlalchemy import MetaData
metadata_obj = MetaData()  # related tables should belong to the same metadata object

from sqlalchemy import Table, Column, Integer, String
user_table = Table(
    "user_account",
    metadata_obj,  # this way the table assigns itself to Metadata collection
    Column("id", Integer, primary_key=True),  # assigns itself to a table
    Column("name", String(length=30)),
    Column("fullname", String),
)

print(repr(user_table.c.name))  # name knows its table: Column('name', String(length=30), table=<user_account>)
print(user_table.c.keys())

print(repr(user_table.primary_key))

from sqlalchemy import ForeignKey
address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id"), nullable=False),
    Column("email_address", String, nullable=False),
)

from sqlalchemy import create_engine
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
metadata_obj.create_all(engine)

# now the same, but with orm

from sqlalchemy.orm import registry
mapper_registry = registry()

print(mapper_registry.metadata)  # MetaData()

Base = mapper_registry.generate_base()

# getting the same Base can be achieved in one step:
# from sqlalchemy.orm import declarative_base
# Base = declarative_base()

from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "user_account"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=30))
    fullname = Column(String)

    addresses = relationship("Address", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"))

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


print(repr(User.__table__))

sandy = User(name="sandy", fullname="Sandy Cheeks")
print(repr(sandy))

# if we had not emitted metadata_obj.create_all(), we should've done
# mapper_registry.metadata.create_all(engine)
# or
# Base.metadata.create_all(engine)
# metadata object is present everywhere

# hybrid tables

class UserHybridTable(Base):
    __table__ = user_table

    addresses = relationship("AddressHybridTable", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class AddressHybridTable(Base):
    __table__ = address_table

    user = relationship("UserHybridTable", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

john = UserHybridTable(name="john", fullname="John Doe")
print(repr(john))

# cross-engine table reflection

engine_1 = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
metadata_1 = MetaData()
table_1 = Table(
    "reflected_table",
    metadata_1,
    Column("id", Integer, primary_key=True),
    Column("column", String),
)
metadata_1.create_all(engine_1)

engine_2 = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
metadata_2 = MetaData()
table_2 = Table(
    "reflected_table",
    metadata_2,
    autoload_with=engine_1,
)
metadata_2.create_all(engine_2)

print(table_2.c.column)
