#coding=utf8
'''
@author: Bright
@description: This shows how to use bs4 and urllib2 to crawl news page from sina website.
In this program, all url are put in a queue. The visited url will be put into a set named
visited. So the same url will not be visited twice.
When crawling web page, many unexpected thing may happen. So when any unexpected thing
happened, I use try and expert to catch it, and ignore this accident. try and expert are 
really helpful techniques when you processing these complicated things.
'''

import urllib2
import gzip
import StringIO
from bs4 import BeautifulSoup

def decodePage(page):
    encoding = page.info().get("Content-Encoding")
    try:
        if encoding in ('gzip', 'x-gzip', 'deflate'):
            content = page.read()
            if encoding == 'deflate':
                data = StringIO.StringIO(zlib.decompress(content))
            else:
                data = gzip.GzipFile('', 'rb', 9, StringIO.StringIO(content))
            page = data.read()
        return page
    except:
        return None

def getPage(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('Accept-Encoding', 'gzip,deflate')]
    try:
        usock = opener.open(url)
        url = usock.geturl()
        data = decodePage(usock)
        usock.close()
        return data
    except:
        return None

def extractLinks(content):
    try:
        soup = BeautifulSoup(content, from_encoding='utf8')
        links = []
        for link in soup.find_all('a'):
            link = link.get('href')
            links.append(link)
        return links
    except:
        return None
    
def extractArticle(content):
    try:
        fields = {}
        soup = BeautifulSoup(content, from_encoding='utf8')
        ans = soup.find_all('meta')
        for line in ans:
            if line.get('property')!=None and line.get('content')!=None:
                if line.get('property') == 'og:type':
                    fields['type'] = line.get('content')
                elif line.get('property') == 'og:title':
                    fields['title'] = line.get('content')
                elif line.get('property') == 'og:description':
                    fields['description'] = line.get('content')
                elif line.get('property') == 'og:url':
                    fields['url'] = line.get('content')
            elif line.get('name')!=None and line.get('content')!=None:
                if 'article:create_at' in line.get('name'):
                    fields['create_at'] = line.get('content')
                elif 'article:update_at' in line.get('name'):
                    fields['update_at'] = line.get('content')
        article = unicode('')
        if fields['type'] == 'article':
            print 'This is a article'
            text = soup.find_all('p')
            for item in text:
                if item.get('class'):
                    article += unicode(item.string) + u'\n'
                    break
                article += unicode(item.string) + u'\n'
            fields['text'] = article
            return fields
        else:
            return None
    except:
        return None

ATTRIS = ['type', 'title', 'description', 'url', 'create_at', 'update_at', 'text']
def writeArticle(fields, name):
    f = open('E:\\workspace\\Baike\\src\\news\\' + name, 'w')
    if fields == None:
        return
    for attri in ATTRIS:
        line = unicode(attri) + u':'
        if attri in fields:
            line += (fields[attri] + u'\n')
        else:
            line += unicode('None\n')
        f.write(line.encode('utf8'))
    f.close()
    
visited = set()
queue = []
def crawling():
    cnt = 1
    queue.append('http://news.sina.com.cn/c/2015-01-14/184231399763.shtml')
    while len(queue) > 0 and cnt < 3000:
        url = queue[0]
        queue.pop(0)
        visited.add(url)
        try:
            print 'getPage %s ...' %(url.encode('GB18030'))
        except:
            print 'page url invaild...'
            continue
        data = getPage(url)
        if data == None:
            continue
        try:    
            data = data.decode('GB18030', 'ignore')
            data = data.encode('utf8')
        except:
            continue
        
        links = extractLinks(data)
        if links != None:
            for link in links:
                if link not in visited:
                    queue.append(link)
        fields = extractArticle(data)
        if fields != None:
            print '-----------writeArticle %d' %(cnt)
            writeArticle(fields, str(cnt))
            cnt += 1

if __name__ == '__main__':
    crawling()
    
def test():
    getPage('test')
    data = getPage('http://news.sina.com.cn/c/2015-01-14/184231399763.shtml')
    data = data.decode('GB18030', 'ignore')
    data = data.encode('utf8')
    links = extractLinks(data)
    for link in links:
        print link
    fields = extractArticle(data)
    if fields != None:
        writeArticle(fields, '1')
    