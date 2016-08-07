# -*- coding: utf-8 -*-
from ..items import *
import scrapy
import logging
import urlparse


class TorecSpider(scrapy.Spider):

    name = "torec"
    allowed_domains = ["torec.net"]
    MAX_PAGE = 711  # 711
    start_urls = 'http://www.torec.net/movies_subs.asp?p={}'

    def start_requests(self):
        for x in xrange(1, TorecSpider.MAX_PAGE):
            yield scrapy.Request(TorecSpider.start_urls.format(x), callback=self.parse, meta={'page': x})

    def parse(self, response):
        full_domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse.urlparse(response.url))
        query_parsed = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        if "page" in response.meta.keys():
            page = response.meta['page']
        elif "p" in query_parsed.keys():
            page = query_parsed['p']
        else:
            page = None

        logging.info('Main: Parsing {}/{}'.format(page, TorecSpider.MAX_PAGE))

        movies_list = response.xpath('//div[@class="sub_tbox"]/div[@class="sub_box"]/div[@class="name"]/a/@href').extract()
        movies_list_length = len(movies_list)
        for index, movie in enumerate(movies_list):
            yield scrapy.Request("{}{}".format(full_domain, movie),
                                 callback=self.parse_movie,
                                 meta={
                                     'page': response.url,
                                     'index': index+1,
                                     'movies_list_length': movies_list_length
                                 })

    def parse_movie(self, response):
        query_parsed = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        if "page" in response.meta.keys():
            page = response.meta['page']
        else:
            page = None

        index = response.meta['index']
        movies_list_length = response.meta['movies_list_length']

        logging.info('Movie: Parsing {}/{}'.format(index, movies_list_length))
        movie = TorecItem()
        movie["search_url"] = page
        movie["url"] = response.url
        movie["serialNum"] = query_parsed.get('sub_id', [response.url])[0]
        if response.xpath('//h1/text()').extract_first():
            movie["name"] = response.xpath('//h1/text()').extract_first()
        else:
            movie["name"] = ""
        if response.xpath('//bdo[@dir="ltr"]/text()').extract_first():
            movie["name_eng"] = response.xpath('//bdo[@dir="ltr"]/text()').extract_first()
        else:
            movie["name_eng"] = ""

        if response.xpath('//div[@class="sub_name_div"]/text()').extract_first():
            movie["summary"] = response.xpath('//div[@class="sub_name_div"]/text()').extract_first()
        else:
            movie["summary"] = ""

        movie_information = [line.strip() for line in response.xpath('//span[@class="sub_name_span"]/text()').extract()]
        movie_information.pop(0)
        movie_information_meta = [m.encode('utf-8') for m in response.xpath('//span[@class="sub_name_span"]/strong/text()').extract()]
        try:
            movie["year"] = movie_information[movie_information_meta.index("שנה:")]
        except ValueError:
            movie["year"] = ""

        try:
            movie["length"] = movie_information[movie_information_meta.index("אורך:")].split(' ')[0]
        except ValueError:
            movie["length"] = ""

        try:
            movie["genres"] = ';'.join([genre.strip() for genre in movie_information[movie_information_meta.index("ז'אנר:")].split('/')])
        except ValueError:
            movie["genres"] = ""

        try:
            movie["producer"] = movie_information[movie_information_meta.index("במאי:")]
        except ValueError:
            movie["producer"] = ""

        movie["actors"] = ';'.join([actor.strip() for actor in response.xpath('//span[@class="sub_name_span"]/a[contains(@href,"person")]/text()').extract()])
        if response.xpath('//div[@class="sub_rank_div"][img[contains(@src,"IMDB")]]/img[1]/@alt').extract_first():
            movie["imdb_score"] = response.xpath('//div[@class="sub_rank_div"][img[contains(@src,"IMDB")]]/img[1]/@alt').extract_first()
        else:
            movie["imdb_score"] = ""
        if response.xpath('//div[@class="sub_info_bar"]/text()').extract():
            movie["downloads"] = response.xpath('//div[@class="sub_info_bar"]/text()').extract()[1].split(':')[1].strip()
        else:
            movie["downloads"] = ""
        yield movie
