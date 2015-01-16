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
        else:
            page = page.read()
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
    f = open('E:\\workspace\\Baike\\src\\news3\\' + name, 'w')
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
def crawling(url = 'http://news.sina.com.cn/'):
    cnt = 1
    queue.append(url)
    visited.add(url)
    while len(queue) > 0:
        url = queue[0]
        queue.pop(0)
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
                    visited.add(link)
        fields = extractArticle(data)
        if fields != None:
            print '-----------writeArticle %d' %(cnt)
            writeArticle(fields, str(cnt))
            cnt += 1

def test(url):
    data = getPage(url)
    data = data.decode('GB18030', 'ignore')
    data = data.encode('utf8')
    #links = extractLinks(data)
    #for link in links:
    #    print link
    fields = extractArticle(data)
    if fields != None:
        for item in fields:
            print item, ':', fields[item].encode('utf8')

if __name__ == '__main__':
    test('http://ent.sina.com.cn/m/c/2015-01-15/doc-icczmvun4987366.shtml')
    #crawling('http://roll.news.sina.com.cn/s/channel.php?ch=01#col=89&spec=&type=&ch=01&k=&offset_page=0&offset_num=0&num=60&asc=&page=1')
    
   