from sqlalchemy import *
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import urllib2
from bs4 import BeautifulSoup as bs
from BaseHTTPServer import HTTPServer
import cgi, cgitb

cgitb.enable()
db = create_engine('sqlite:///story.db', echo=False)
print 'made the database engine and stuff'
metadata = MetaData()
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Story(Base):
    __tablename__ = 'stories'
    storyID = Column(Integer)
    creatorID = Column(Integer)
    parentID = Column(Integer)
    textID = Column(Integer, primary_key = True)
    text = Column(String)
    keyword=Column(String)
    
    def __init__(self, storyID, creatorID, parentID, text):
        self.storyID = storyID
        self.creatorID = creatorID
        self.parentID = parentID
        self.text = text
        keyword=Column(String)
    

class Creator(Base):
    __tablename__ = 'creators'
    creatorID = Column(Integer, primary_key = True)
    name = Column(String)
    password = Column(String)

    def __init__(self, name, password):
        self.name = name
        self.password = password

class ParentChild(Base):
    __tablename__ = 'parent_child'
    parentID = Column(Integer)
    childID = Column(Integer)
    ID = Column(Integer, primary_key = True)
    
    def __init__(self, parentID, childID):
        self.parentID = parentID
        self.childID = childID

Base.metadata.create_all(db)

def getStory(storyID):
    #print "I'm going to find this story: " + storyID
    print "finding story nodes"
    text = []
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(bind=db)
    Session = session()
    results = Session.query(Story).filter_by(storyID = storyID).all()
    for result in results:
         text.append(result.text + '  ')

    return text

def addNode(stID, pID, cID, words, keyword):
    #print "I'm adding a node to " + storyID + " after " + parentID + " written by " + creatorID + " containing " + text
    while words
    print "adding a story node"
    first = words.pop()
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(bind=db)
    Session = session()
    newNode = Story(storyID = stID, parentID = pID, creatorID = cID, text = first, keyword=keyword)
    Session.add(newNode)
    Session.commit()
    newNode = Session.query(Story).filter_by(storyID = stID, parentID = pID, creatorID = cID, text = first, keyword= keyword).first()
    newRelation = ParentChild(parentID = pID, childID = newNode.textID)
    Session.add(newRelation)
    Session.commit()
    return True;
    
class GetHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        print "options!"
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
    
    def do_GET(self):
        print "get"
        try:
            parsed_path = urlparse.urlparse(self.path)
            reqtype = parsed_path.path.split('/')[1]
            print reqtype
            if reqtype == 'samplepage':
                with open("/home/senortubes/public_html/samplepage.html", "r") as myfile:
                    data = myfile.read()
                    #print data
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)

        except IOError:
            print "OOPSY DAISY"
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        print "POST!"
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                postvars = cgi.parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            print postvars
            reqtype = postvars['reqType']
            if reqtype == 'getStory':
                storyID = postvars['storyNum']
                #print storyID
                storynodes = getStory(storyID)
                #for node in storynodes:
                 #   print node

                self.send_response(200)
                self.end_headers()
                self.wfile.write(storynodes)   
            if reqtype == 'submitNode':
                storyID = postvars['storyNum']
                parentID = postvars['textID']
                creatorID = '1'
                text = postvars['text']
                import re
                sentenceEnders = re.compile('[.!?]')
                sentences = sentenceEnders.split(text)
                for sentence in sentences:
                    if addNode(storyID, parentID, creatorID, sentence) == False:
                        print "READ IN PROBLEM"
                        self.send_error(500, 'Internal Server Error: %s' % self.path)
                    #print sentence
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Committed successfully!")

            return

        except IOError:
            print "OOPSY DAISY"
            self.send_error(404, 'File Not Found: %s' % self.path)

def main():
    try:
        server = HTTPServer(('0.0.0.0', 8083), GetHandler)
        print 'Starting server, use <Ctrl-C> to stop'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down'
        server.socket.close()

if __name__ == '__main__':
    main()
