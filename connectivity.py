import sqlalchemy

print(sqlalchemy.__version__)  # 1.4.28

from sqlalchemy import create_engine  # performs lazy initialization of the engine
engine = create_engine(  # engine is a connection factory
    "sqlite+"  # the actual DBMS used
    "pysqlite://"  # the DB API interface
    "/:memory:",  # the location of the database -- no files created
    echo=True,  # print SQL emitted for debugging purposes
    future=True  # use 2.0 features even though we are 1.4
)

from sqlalchemy import text

with engine.connect() as connection:  # open resource against the database
    result = connection.execute(text("select 'hello world'"))
    print(result.all())
    # ROLLBACK is emitted

with engine.connect() as connection:
    connection.execute(text("CREATE TABLE some_table (x int, y int)"))
    connection.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 2}],
    )
    # "commit as you go" style
    connection.commit()  # COMMIT is emitted


# "begin once" style
with engine.begin() as connection:
    connection.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )
    # COMMIT is emitted

with engine.connect() as connection:
    result = connection.execute(text("SELECT x, y from some_table"))
    for row in result:  # result is iterable
        print(f"{row.x=} {row.y=}")
    # other ways to iterate the results:
    for x, y in result:  # result is empty because we exhausted it
        print(f"{x=} {y=}")
    for row in result:
        print(f"{row[0]=} {row[1]=}")
    for row in result.mappings():
        print(f"{row['x']=} {row['y']=}")


statement = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6)
with engine.connect() as connection:
    result = connection.execute(statement)
    for row in result:
        print(f"{row.x=} {row.y=}")

from sqlalchemy.orm import Session

# when session is passed non-ORM stuff, it behaves almost like Connection:
statement = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y").bindparams(y=6)
with Session(engine) as session:
    result = session.execute(statement)
    for row in result:
        print(f"{row.x=} {row.y=}")

with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}]
    )
    session.commit()  # after the end of the transaction, session disposes of the connection
