# -*- coding: utf-8 -*-
# @Time    : 2016/8/4
# @Author  : rain
import codecs
import logging
import re
import time
import urllib.request
import urllib.parse

import pandas as pd
from pyquery import PyQuery as pq


def quote_url(model_name):
    base_url = "https://www.sogou.com/web?query=%s"
    site_zol = "site:detail.zol.com.cn "
    return base_url % (urllib.parse.quote(site_zol + model_name))


def parse_sogou(model_name):
    search_url = quote_url(model_name)
    request = urllib.request.Request(url=search_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/45.0.2454.101 Safari/537.36'})
    sogou_html = urllib.request.urlopen(request).read()
    sogou_dom = pq(sogou_html)
    goto_url = sogou_dom("div.results>.vrwrap>.vrTitle>a[target='_blank']").eq(0).attr("href")
    logging.warning("goto url: %s", goto_url)
    if goto_url is None:
        return None
    goto_dom = pq(url=goto_url)
    script_text = goto_dom("script").text()
    zol_url = re.findall(r'\("(.*)"\)', script_text)[0]
    return zol_url


def parse_zol(model_name):
    zol_url = parse_sogou(model_name)
    if zol_url is None:
        return None, None
    zol_html = urllib.request.urlopen(zol_url).read()
    zol_dom = pq(zol_html)
    title = zol_dom(".page-title.clearfix")
    name = title("h1").text()
    alias = title("h2").text()
    if u'（' in name:
        match_result = re.match(u'(.*)（(.*)）', name)
        name = match_result.group(1)
        alias = match_result.group(1) + " " + alias
    return name, alias


if __name__ == "__main__":
    result_list = []
    with codecs.open("./resources/data.txt", 'r', 'utf-8') as f:
        for model in f.readlines():
            time.sleep(10)
            model = model.rstrip()
            label_name, label_alias = parse_zol(model)
            logging.warning("model: %s, name: %s, alias: %s", model, label_name, label_alias)
            result_list.append({'model': model, 'name': label_name, 'alias': label_alias})
        df = pd.DataFrame(result_list, columns=['model', 'name', 'alias'])
        df.to_csv("./resources/result.csv", index=False, header=False)
