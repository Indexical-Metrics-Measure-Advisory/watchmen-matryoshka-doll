from sqlalchemy import create_engine

engine = create_engine("mysql+mysqldb://root:123456@localhost:3306/watchmen",
                       echo=True,
                       future=True,
                       pool_recycle=3600)
