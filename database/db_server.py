from sqlalchemy import *
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import urllib2
from bs4 import BeautifulSoup as bs
from BaseHTTPServer import HTTPServer
from cookielib import Cookie
from cookielib import CookieJar
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
    
    def __init__(self, storyID, creatorID, parentID, text):
        self.storyID = storyID
        self.creatorID = creatorID
        self.parentID = parentID
        self.text = text
    

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
    ID = Column(Integer, primary_key = True)
    parentID = Column(Integer)
    childID = Column(Integer)
    
    def __init__(self, parentID, childID):
        self.parentID = parentID
        self.childID = childID

Base.metadata.create_all(db)

class Node:
    def __init__(self, textID, text, children):
        self.textID = textID
        self.text = text
        self.children = children
    def dict(self):
        nodeDict = {}
        nodeDict['textID'] = self.textID
        nodeDict['text'] = self.text
        nodeDict['children'] = self.children
        return nodeDict

def getStory(storyID):
    #print "I'm going to find this story: " + storyID
    print "finding story nodes"
    text = []
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(bind=db)
    Session = session()
    results = Session.query(Story).filter_by(storyID = storyID).all()
    
    resultDict = {}
    parent = None
    for result in results:
        children = []
        child = Session.query(ParentChild).filter_by(parentID = result.textID).all()
        print result.parentID
        for things in child:
                #print things[1]
            children.append(things.childID)
           
            
        newNode = Node(result.textID, result.text, children)
        resultDict[str(result.textID)] = newNode.dict()
        if result.parentID == 1:
            parent = result
    print resultDict
    storyDict = {}
    storyDict['name'] = storyID
    storyDict['contents'] = resultDict
    storyDict['root'] = Node(parent.textID, result.text, children).dict()
    return storyDict

def getStoryList():
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(bind=db)
    Session = session()
    retList = []
    storylist = Session.query(Story).all()
    for item in storylist:
        if item.storyID not in retList:
            retList.append(item.storyID)
    return retList

def findLargestStoryID():
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker(bind=db)
    Session = session()
    retval = 0
    storylist = Session.query(Story).all()
    for item in storylist:
        if item.storyID > retval:
            retval = item.storyID
    return retval

def addNode(stID, pID, cID, words):
    #print "I'm adding a node to " + storyID + " after " + parentID + " written by " + creatorID + " containing " + text
    if words == '' or len(words) == 0:
        print "Story has been stored!"
        print pID
        return True;
    else:
        from sqlalchemy.orm import sessionmaker
        basicID = 0
        first = words.pop(0)
        session = sessionmaker(bind=db)
        Session = session()
        newNode = Story(storyID = stID, parentID = pID, creatorID = cID, text = first)
        Session.add(newNode)
        Session.commit()
        newNode = Session.query(Story).filter_by(storyID = stID, parentID = pID, creatorID = cID, text = first).first()
        basicID = newNode.textID
        newRelation = ParentChild(parentID = pID, childID = newNode.textID)
        Session.add(newRelation)
        Session.commit()
        addNode(stID, basicID, cID, words)


            
C = {}
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
            
            storynum = parsed_path.query
            host = self.client_address[0]
            print host
            C[str(host)]= storynum
            #print "the additional args are: " +C[str(host)]
            #print "the reqtype is " + reqtype
            if reqtype == 'samplepage':
                with open("/home/senortubes/public_html/samplepage.html", "r") as myfile:
                    data = myfile.read()
                    #print data
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
            elif reqtype == 'new_story':
                with open("/home/senortubes/public_html/new_story_page.html", "r") as myfile:
                    data = myfile.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
            elif reqtype == 'view_story':
                with open("/home/senortubes/public_html/view_story.html", "r") as myfile:
                    data = myfile.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
            elif reqtype == 'home':
                with open("/home/senortubes/public_html/home_page.html", "r") as myfile:
                    data = myfile.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
            elif reqtype == 'storylist':
                with open("/home/senortubes/public_html/storylist.html", "r") as myfile:
                    data = myfile.read()
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(data)
            elif reqtype == 'playmockup':
                with open("/home/senortubes/public_html/playmockup.html", "r") as myfile:
                    data = myfile.read()
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
            reqtype = postvars['reqType'][0]
            print reqtype
            if reqtype == 'getStory':
                storyID = postvars['storyNum'][0]
                print storyID
                storynodes = getStory(storyID)
                #retval = ''.join([node for node in storynodes])
                #for node in storynodes:
                #    print node
                print "got story!"
                import json
                print json.dumps(storynodes)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(storynodes))
            if reqtype == 'getStoryNum':
                host = self.client_address[0]
                print "getting story number " + C[str(host)]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(C[str(host)])
            if reqtype == 'getLargestStory':
                print "finding largest story"
                retval = findLargestStoryID()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(retval)
            if reqtype == 'getStoryList':
                print "getting story list"
                retval = getStoryList()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(retval)
            if reqtype == 'submitNode':
                print "submitting node"
                storyID = postvars['storyNum'][0]
                parentID = postvars['initialID'][0]
                creatorID = '1'
                text = postvars['text'][0]
                import re
                sentenceEnders = re.compile('[.!?]')
                sentences = sentenceEnders.split(text)
                useless = sentences.pop()
                print sentences
                if addNode(storyID, parentID, creatorID, sentences) == False:
                    print "READ IN PROBLEM"
                    self.send_error(500, 'Internal Server Error: %s' % self.path)
                print "Story has been stored!"
                storynodes = getStory(storyID)
                for node in storynodes:
                    print node
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
