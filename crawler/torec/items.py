# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class TorecItem(scrapy.Item):
    # define the fields for your item here like:

    search_url = scrapy.Field()
    serialNum = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    name_eng = scrapy.Field()
    summary = scrapy.Field()
    year = scrapy.Field()
    length = scrapy.Field()
    genres = scrapy.Field()
    producer = scrapy.Field()
    actors = scrapy.Field()
    imdb_score = scrapy.Field()
    downloads = scrapy.Field()
