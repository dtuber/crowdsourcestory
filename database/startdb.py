from sqlalchemy import *

db = create_engine('sqlite:///story.db', echo=False)
metadata = MetaData()

stories = Table('stories', metadata,
	Column('storyID', Integer),
	Column('creatorID', Integer),  #needs to be rowid
	Column('parentID', Integer),   #needs to be rowid
	Column('textID', Integer, primary_key=True),
	Column('text', String)
	#sqlite_autoincrement=True)
)

creators = Table('creators', metadata,
        Column('creatorID', Integer),
        Column('name', String),
        Column('userID', Integer, primary_key=True),
        Column('password', String)
)

children = Table('parent_child', metadata,
        Column('parentID', Integer),
        Column('childID', Integer)
)

metadata.create_all(db)
dbConn = db.connect()

test =stories.insert().values(storyID=0, creatorID=0, parentID=0, text='this is a test string')
insertId = dbConn.execute(test).inserted_primary_key

print insertId

