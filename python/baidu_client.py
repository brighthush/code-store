#coding:gbk
import urllib2
import gzip
import StringIO
import json

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

def writeFile(des, content):
    f = open(des, 'w')
    #content = content.decode('utf8', 'ignore').encode('gbk', 'ignore')
    f.write(content)
    f.close()

# 请求本地新闻列表
def call_localnewslist():
    print 'call_localnewslist ...'
    header = {'Accept-Encoding':'gzip', 'User-Agent':'bdnews_android_phone', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8' }
    url = 'http://api.baiyue.baidu.com/sn/api/localnewslist'
    content = 'loc=0&ln=200&cuid=FDDAAE979F6FBC2704CCAD5AA64289F6%7C000000000000000&ver=2&mid=000000000000000_08%3A00%3A27%3A25%3A81%3A6c&wf=1&an=20&'
    request = urllib2.Request(url, data=content, headers=header)
    response = urllib2.urlopen(request)
    print response.info().get('Content-Encoding')
    the_page = decodePage(response)
    the_page = json.loads(the_page)
    print the_page['errno']
    data = the_page['data']
    news = data['news']
    print len(news)
    print 'finished call_localnewslist ...'

# 请求特定主题
def call_recommendlist(topic='社会'):
    pass

# 请求新闻内容
def call_localnewsinfo(nids):
    pass

# 请求新闻评论
# get comments by news id
def call_getcomments(nid='8051110759019602749'):
    print 'call_getcomments ...'
    header = {}
    url = 'http://api.baiyue.baidu.com/sn/api/getcomments?'
    paras = 'nid=' + nid + '&order=time&from=info&ts=0&pn=20&ver=2'
    url += paras
    request = urllib2.Request(url, headers=header)
    response = urllib2.urlopen(request)
    the_page = decodePage(response)
    the_page = json.loads(the_page)
    errno = the_page['errno']
    data = the_page['data']
    hasmore = data['hasmore']
    comments = data['comments']
    print errno, hasmore, len(comments)
    print 'finished call_getcomments ...'
    
if __name__ == '__main__':
    call_localnewslist()
    #call_getcomments()
    #print 'write file...'
    #writeFile('E:\\GitHub\\code-store\\python\\data.out', the_page)
    #print 'wrote file...'
    