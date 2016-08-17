#coding=utf-8
import codecs
import logging
import re
import time
import urllib.request
import urllib.parse
import random
##import pandas as pd
from pyquery import PyQuery as pq
import timeout_decorator


def quote_url(model_name):
    base_url = "https://www.sogou.com/web?query=%s"
    site_zol = "site:detail.zol.com.cn "
    return base_url % (urllib.parse.quote(site_zol + model_name))

@timeout_decorator.timeout(30)
def parse_sogou(model_name):
    try:
        search_url = quote_url(model_name)
        headerset = [{"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
               "Accept":"text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8"},
                     {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' 'Chrome/45.0.2454.101 Safari/537.36'},
                     {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/52.0.2743.116 Safari/537.36"},
                     {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586"},
                     {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"},
                     {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"},
                     {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}]
        x = random.choice(headerset)
##        print(x)
        request = urllib.request.Request(url=search_url, headers=x)
        sogou_html = urllib.request.urlopen(request).read()
        sogou_dom = pq(sogou_html)
        goto_url = sogou_dom("div.results>.vrwrap>.vrTitle>a[target='_blank']").eq(0).attr("href")
##        logging.warning("goto url: %s", goto_url)
        if goto_url is None:
            return None
        goto_dom = pq(url=goto_url)
        script_text = goto_dom("script").text()
        zol_url = re.findall(r'\("(.*)"\)', script_text)[0]
        return zol_url
    except Exception as e:
        print(str(e))

@timeout_decorator.timeout(30)
def parse_zol(model_name):
    try:
        zol_url = parse_sogou(model_name)
        if zol_url is None:
            return None, None
        zol_html = urllib.request.urlopen(zol_url).read()
        zol_dom = pq(zol_html)
        title = zol_dom(".page-title.clearfix")
        name = title("h1").text()
        alias = title("h2").text()
        if u'（' in name:
            match_result = re.match(u'(.*)（(.*)', name)
            name = match_result.group(1)
            alias = match_result.group(2) + " " + alias
        return str(name), str(alias)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    brand = "dvc"
    i = 1
    inputname, logname = brand + ".txt", brand + "log"    
    with open(inputname) as f:
        for model in f:
            try:
                print(i)
                model = model.strip()
                label_name, label_alias = parse_zol(model)
                if label_name is None:
                    label_name, label_alias = parse_zol(model)
                logging.warning("model: %s, name: %s, alias: %s", model, label_name, label_alias)
                with open(logname, "a") as data:
                    print(str(model) + "," + str(label_name) + "," + str(label_alias), file = data)
                i += 1
##                time.sleep(random.randrange(2, 4))
            except Exception as e:
                print(str(e))
                continue
