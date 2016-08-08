# -*- coding: utf-8 -*-
import string
import re
from tabulate import tabulate
from collections import OrderedDict
import os
import codecs
import math
from operator import itemgetter
from utils import UnicodeWriter
from runTagger import run_meni

k1 = 1.5
b = 0.75
ENGLISH_TEST = False
HEBREW_TEST = True
FILES_DIRECTORY = "files_eng_2" if ENGLISH_TEST else "files_test" if HEBREW_TEST else "files"
FREQUENCY_HEADERS = ["Token", "Times", "In Files", "IDF"]
# TODO: rebuild class upon previous results
'''
 TODO: add bm25
 http://terrier.org/docs/v2.2.1/javadoc/uk/ac/gla/terrier/matching/models/BM25.html
 https://dato.com/products/create/docs/generated/graphlab.toolkits.feature_engineering.BM25.transform.html
 https://dato.com/products/create/docs/generated/graphlab.text_analytics.bm25.html
 lectures ' the vector models'
'''


STOPWORDS_FILE = 'moviesstopwords.txt'
FREQUENCY_FILE = 'moviesFrequencyFile.csv'
INDEX_FILE = 'index.csv'


def get_stop_words():
    stopwords = codecs.open(STOPWORDS_FILE, 'r+', encoding='utf-8').readlines()
    stopwords = [stripped.strip() for stripped in stopwords]
    tagged = run_meni(' '.join(stopwords))
    return tagged

STOPWORDS = get_stop_words()


class Movie(object):
    def __init__(self):
        self.file = map(lambda x: os.path.join(FILES_DIRECTORY, x),
                        filter(lambda x: x == INDEX_FILE, os.listdir(FILES_DIRECTORY)))[0]
        self.movies = {}
        self._parse()

    def _parse(self):
        import csv
        def unicode_csv_reader(**kwargs):
            csv_reader = csv.reader(open(self.file), dialect=csv.excel, **kwargs)
            for row in csv_reader:
                yield [cell.decode('utf-8') for cell in row]
        data = unicode_csv_reader()
        data.next()
        for movies in data:
            serialNum, search_url, url, name_eng, name, \
            genres, length, year, imdb_score, downloads, \
            producer, actors = movies
            self.movies[serialNum] = OrderedDict([
                ("serialNum", serialNum),
                # ("search_url", search_url),
                ("url", url),
                ("name_eng", name_eng),
                # ("name", name),
                # ("genres", genres),
                ("length", length),
                ("year", year),
                ("imdb_score", imdb_score),
                ("downloads", downloads),
                # ("producer", producer),
                # ("actors", actors)
            ])

    def get_movie(self, movie_id):
        return self.movies[str(movie_id)]

    def print_movie(self, movie_id, additional_dict=None):
        if isinstance(movie_id, str):
            movie = self.get_movie(movie_id)
            if additional_dict:
                movie.update(additional_dict)
            print tabulate([movie.values()], headers=movie.keys(), tablefmt='fancy_grid')
        elif hasattr(movie_id, '__iter__'):
            movies = self.get_movies(movie_id)
            movies_cpy = movies
            if additional_dict:
                for movie in movies_cpy:
                    if str(movie['serialNum']) in additional_dict:
                        movie.update(additional_dict[str(movie['serialNum'])])
            print tabulate(movies, headers="keys", tablefmt='fancy_grid')

    def get_movies(self, movie_ids):
        return [self.get_movie(movie_id) for movie_id in movie_ids]


class DBIndexer(object):

    def __init__(self):
        self.words_dict = dict()
        self.files = map(lambda x: os.path.join(FILES_DIRECTORY, x),
                         filter(lambda x: x != INDEX_FILE, os.listdir(FILES_DIRECTORY)))
        self.index_file = os.path.join(FILES_DIRECTORY, INDEX_FILE)
        self.movies_ids = list()
        self.avdl = 0

    @staticmethod
    def get_term_frequency(term, split_doc):
        return float(('%0.6f' % (split_doc.count(term) / float(len(split_doc)))).rstrip('0'))

    @staticmethod
    def score_bm25(n, ttl_files, f, dl, avg_dl):
        """
        :param n: is the number of documents containing q{i}
        :param ttl_files: total number of documents in the collection
        :param f: is the term frequency in the document
        :param dl: is the number of words in the document
        :param avg_dl: is the average number of words per document in the corpus
        :return:
        """
        # TEST:
        # while N(ttl_files)-n < n:
        #     n -= 1

        # log((N-n(qi) + 0.5) / (n(qi) + 0.5)) | aka 'idf'
        first = math.log(float(ttl_files - n + 0.5) / float(n + 0.5))

        # f(qi)*(k1+1) / k1 * [( 1-b ) + b * (|D| / DaVG)]
        second = ((k1 + 1) * f) / ((k1 * ((1-b) + b * (float(dl) / float(avg_dl)))) + f)

        # return math.fabs(first) * second
        return first * second

    @staticmethod
    def _dot(query_v, doc_v):
        query_v_sum = 0
        doc_v_sum = 0
        for v in query_v:
            query_v_sum += math.pow(v, 2)
        query_v_sqrt = math.sqrt(query_v_sum)
        for v in doc_v:
            doc_v_sum += math.pow(v, 2)
        doc_v_sqrt = math.sqrt(doc_v_sum)

        query_doc = query_v_sqrt * doc_v_sqrt

        if query_doc == 0:
            return 0

        dot_product = sum(i[0] * i[1] for i in zip(query_v, doc_v))

        return dot_product / float(query_doc)

    @staticmethod
    def split_document(document):
        if ENGLISH_TEST:
            return [token for token in document.lower().split()]

        tokens = list()
        for token in filter(lambda x: x, re.split(r';|\.|,|\s|\W', document, flags=re.UNICODE)):
            if token in STOPWORDS:
                continue
            token = token.strip(string.punctuation).strip()
            if not re.search('[a-zA-Z|0-9]', token) and len(token) > 1:
                tokens.append(token)
        return tokens

    def _parse_file(self, file_name, content):
        split_document_list = DBIndexer.split_document(content)
        self.movies_ids.append(file_name)
        self.avdl += len(split_document_list)
        tagged_doc_list = run_meni(u' '.join(split_document_list))
        for token in tagged_doc_list:
            if token not in self.words_dict:
                self.words_dict[token] = {
                    'times': 1,
                    file_name: DBIndexer.get_term_frequency(token, tagged_doc_list)
                }
            elif file_name not in self.words_dict[token]:
                self.words_dict[token][file_name] = DBIndexer.get_term_frequency(token, tagged_doc_list)
                self.words_dict[token]['times'] += 1
            else:
                continue

    def _get_movies_id_from_words_dict(self, token):
        return list(set(self.words_dict.get(token, [])).difference(['times', 'idf']))

    def export_data(self):
        f = open(FREQUENCY_FILE, 'wb')
        f.write(codecs.BOM_UTF8)
        frequency_writer = UnicodeWriter(f)
        frequency_writer.writerow(FREQUENCY_HEADERS)
        for word_idx, token in enumerate(self.words_dict, start=1):
            # print(u"Exporting word (%d/%d): [%s]" % (word_idx, len(self.words_dict), token))
            occurs_list = [(key, self.words_dict[token][key]) for key in self._get_movies_id_from_words_dict(token)]
            frequency_writer.writerow([
                token.decode('utf-8'),
                self.words_dict[token]['times'],
                ';'.join(['{}-{}'.format(movie_id, occurs) for movie_id, occurs in occurs_list]),
                self.words_dict[token]['idf']
            ])
        return self

    @staticmethod
    def _count_token_in_movie(token, movie_id):
        codecs_open = codecs.open(os.path.join(FILES_DIRECTORY, movie_id), encoding='utf-8')
        split_document_list = DBIndexer.split_document(codecs_open.read())
        tagged_doc_list = run_meni(' '.join(split_document_list))
        return tagged_doc_list.count(run_meni(token)[0]), len(tagged_doc_list)

    def bm25(self, query, k):
        print(u"Step #3: Calculating BM25: '%s'" % query)
        split_doc = DBIndexer.split_document(query)
        ttl_files = len(self.files)
        avg_dl = self.avdl
        results = list()
        for movie_id in self.movies_ids:

            tmp_score = list()
            for q in split_doc:
                n = len(self._get_movies_id_from_words_dict(q))
                f, dl = DBIndexer._count_token_in_movie(q, movie_id)
                score = DBIndexer.score_bm25(n, ttl_files, f, dl, avg_dl)
                tmp_score.append(score)
            results.append((movie_id, sum(tmp_score)))

        return sorted(results, key=itemgetter(1), reverse=True)[:k]

    def query_similarity_vector(self, query, k):
        query_split = DBIndexer.split_document(query)
        query_tag = run_meni(query_split)
        query_dict = dict()
        print("Step #3: Calculating TF * IDF")
        for q in query_tag:
            tf = DBIndexer.get_term_frequency(q, query_tag)
            idf = self.words_dict[q]['idf'] if q in self.words_dict else 0
            movies_id_list = self._get_movies_id_from_words_dict(q)
            if not movies_id_list:
                query_dict[q] = {
                    'tf': -1,
                    'idf': -1,
                }
                continue
            for movie_id in self._get_movies_id_from_words_dict(q):
                token_tf = self.words_dict[q][movie_id]
                if q not in query_dict:
                    query_dict[q] = {
                        'tf': tf,
                        'idf': idf,
                        movie_id: token_tf * idf
                    }
                elif movie_id not in query_dict[q]:
                    query_dict[q][movie_id] = token_tf * idf

        '''
        query_dict:
            {
                'query1' : {
                        'tf': tf (determined by CosineSimilarity.get_term_frequency(query1, query_split)),
                        idf: : idf (determined by self.words_dict[q]['idf']),
                        'movie_id_1': token_tf * idf (determined by token_tf * idf ),
                        'movie_id_2': token_tf * idf (determined by token_tf * idf ),,
                        ...
                        'movie_id_k': token_tf * idf (determined by token_tf * idf ),,
                        'times': 1
                }
            }
        '''

        print(u"Step #4: Cosine Similarity: '%s'" % query)
        if not query_dict:
            return []
        results = list()
        for movie_id in self.movies_ids:
            query_v = list()
            doc_v = list()
            for q in query_dict:
                if query_dict[q]['idf'] == -1:
                    continue
                query_v.append(query_dict[q]['idf'] * query_dict[q]['tf'])
                doc_v.append(query_dict[q]['idf'] * self.words_dict[q].get(movie_id, 0))
            if not doc_v:
                results.append((movie_id,'0'))
                continue
            if doc_v[0] == 0 and doc_v.count(doc_v[0]) == len(doc_v):
                continue
            results.append((movie_id, ('%.5f' % self._dot(query_v, doc_v))))

        '''
         results:
            [
            (movie_id, match by [0,1]), (movie_id_2, match by [0,1]), ... ,(movie_id_k, match by [0,1])
            ]
        '''
        return sorted(results, key=itemgetter(1), reverse=True)[:k]

    def step_1(self):
        """
        In the end of step 1, self.words_dict will be:
            self.words_dict:
            {
                'word' : {
                        'movie_id_1': tf (determined by CosineSimilarity.get_term_frequency(word, split_document_list)),
                        'movie_id_2': tf (determined by CosineSimilarity.get_term_frequency(word, split_document_list)),
                        ...
                        'movie_id_k': tf (determined by CosineSimilarity.get_term_frequency(word, split_document_list)),
                        'times': k

                }
            }
        """
        print("Step #1: Term Frequency - Parsing %d documents" % (len(self.files)))
        for fn_i, fn in enumerate(self.files, start=1):
            _, filename = os.path.split(fn)
            print("\tDocument: %s (%d/%d)" % (fn, fn_i, len(self.files)))
            codecs_open = codecs.open(fn, encoding='utf-8')
            self._parse_file(filename, codecs_open.read())
            codecs_open.close()

        self.avdl /= float(len(self.movies_ids))
        return self

    def step_2(self):
        """
        In the end of step 2, self.words_dict will be:
            self.words_dict: {
                'word' : {
                        'movie_id_1': tf (determined by CosineSimilarity.get_term_frequency(word, split_document_list)),
                        'movie_id_2': tf (determined by CosineSimilarity.get_term_frequency(word, split_document_list)),
                        ...
                        'movie_id_k': tf (determined by get_term_frequency(word, split_document_list)),
                        idf: : idf (determined by inverse_document_frequency(ttl_Docs , occur times in all docs)),
                        'times': 1
                }
            }
        """
        print("Step #2: Inverting %d Documents" % (len(self.files)))

        def _get_idf(_times):
            if _times == 0:
                return 1.0
            _idf = 1.0 + math.log(len(self.files) / float(_times))
            return float(('%0.9f' % _idf).rstrip('0'))

        for token in self.words_dict:
            times = self.words_dict[token]['times'] if self.words_dict[token]['times'] else 0
            self.words_dict[token]['idf'] = _get_idf(times)
        return self


if __name__ == '__main__':
    mv = Movie()
    cosine = DBIndexer()
    cosine.step_1()
    cosine.step_2()
    while True:
        query = raw_input("Type your query or press q to quit:")
        if query == 'q':
            break
        qsv = cosine.query_similarity_vector(query.decode('utf-8'), 10)
        qsv_movies = [movie_id for movie_id, score in qsv]
        qsv_data = OrderedDict()
        for movie_id, score in qsv:
            qsv_data[movie_id] = OrderedDict([('RANK', score)])
        mv.print_movie(qsv_movies, qsv_data)

        bm25 = cosine.bm25(query.decode('utf-8'), 10)
        bm25_movies = [movie_id for movie_id, score in bm25]
        bm25_data = OrderedDict()
        for movie_id, score in bm25:
            bm25_data[movie_id] = OrderedDict([('RANK', score)])
        mv.print_movie(bm25_movies, bm25_data)

    print("Exporting data")
    cosine.export_data()
