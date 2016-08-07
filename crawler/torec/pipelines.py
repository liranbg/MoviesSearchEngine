# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import os
from unicoding import UnicodeWriter
HEADERS = [
    'serialNum', 'search_url', 'url', 'name_eng', 'name', 'genres', 'length', 'year', 'imdb_score',
    'downloads', 'producer', 'actors'
]
OUTPUT_DIR = "files"


class TorecPipeline(object):
    def __init__(self):
        if not os.path.isdir(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        self.f_indexer = open(os.path.join(OUTPUT_DIR, 'index.csv'), 'wb')
        self.f_indexer.write(codecs.BOM_UTF8)
        self.wrote_headers = False
        self.meta_writer = UnicodeWriter(self.f_indexer)

    def __del__(self):
        self.f_indexer.close()

    def process_item(self, item, spider):
        f = open(os.path.join(OUTPUT_DIR, item['serialNum']), 'wb')

        self.meta_writer.writerows(self._build_row(item, not self.wrote_headers))
        if not self.wrote_headers:
            self.wrote_headers = True

        f.write(item['summary'].encode('utf-8'))
        f.close()

    def _build_row(self, item, return_with_headers=False):
        data = (item[header] for header in HEADERS)
        if return_with_headers:
            return [HEADERS, data]
        return [data]




