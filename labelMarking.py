import urllib
from bs4 import BeautifulSoup as BS
import time
from pyquery import PyQuery as pq
import timeout_decorator
import re
import random

def writeByLine(fileName, content):
    with open(fileName, "a") as f:
        print(content.strip(), file = f)

def genHeader():
    headerset = [{"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
           "Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8"},
                 {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' 'Chrome/45.0.2454.101 Safari/537.36'},
                 {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/52.0.2743.116 Safari/537.36"},
                 {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586"},
                 {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"},
                 {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"},
                 {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}]
    return random.choice(headerset)

def readByLine(f1, f2):
    print("reading")
    with open(f1) as f:
        for i in f:
            i = str(i).strip()
            if i is not None and i != "":
                word = i + ",site:detail.zol.com.cn " + i
                writeByLine(f2, word)
    print("done")

def getHref(word):
    try:
        baseUrl = 'http://www.baidu.com/s'
        page = 1
        data = {'wd':word,
                'pn':str(page-1)+'0',
                'tn':'baidurt',
                'ie':'utf-8',
                'bsst':'1'}
        data = urllib.parse.urlencode(data)
        url = baseUrl+'?'+data
        request = urllib.request.Request(url,headers=genHeader())  
        response = urllib.request.urlopen(request)
        html = response.read()
        soup = BS(html).find_all(class_='f')
        return str(soup[0].find("a").attrs["href"])
    except Exception as e:
        return str(e)

def getInfo(href):
    try:
        href = href.strip()
        zol_html = urllib.request.urlopen(href).read()
        zol_dom = pq(zol_html)
        title = zol_dom(".page-title.clearfix")
        name = title("h1").text()
        alias = title("h2").text()
        if u'（' in name:
            match_result = re.match(u'(.*)（(.*)）', name)
            name = match_result.group(1)
            alias = match_result.group(2) + " " + alias
        return str(name), str(alias)
    except Exception as e:
        return str(e), ""
    
@timeout_decorator.timeout(10)
def crawler(i, f3, f4):
    i = i.strip()
    (model, word) = i.split(",")
    href = getHref(word)
##    print(href)
    writeByLine(f3, i + "," + href)
    name, alias = getInfo(href)
    writeByLine(f4, str(model) + "," + str(name) + "," + str(alias))
    return name
    
def coordinator(i):
    f1 = i + ".txt"
    f2 = i + "clean"
    f3 = i + "href"
    f4 = i + "info"
    n = 1
    #readByLine(f1, f2)
    with open(f2) as f:
        for i in f:
            try:
                name = crawler(i, f3, f4)
                print(str(n) + " " + name)
                n += 1
##                time.sleep()
            except Exception as e:
                print(str(e))
                continue

if __name__ == "__main__":
    coordinator("dvc2")

            
            
        
                
##get1stLink(getHref("zte|q806t"))
