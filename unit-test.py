import unittest
import createFrequency


class CreateFrequency(unittest.TestCase):

    def test_step1_2(self):
        createFrequency.ENGLISH_TEST = True
        createFrequency.FILES_DIRECTORY = "files_eng"
        self.cosine = createFrequency.CosineSimilarity()

        expected_step_1_words_dict = {
            'a': {
                '1': 0.1,
                'times': 1
            },
            'unexamined': {
                '2': 0.142857,
                'times': 1
            },
            'life': {
                '1': 0.1,
                '2': 0.142857,
                'times': 2
            },
            'living': {
                '2': 0.142857,
                'times': 1
            },
            'of': {
                '1': 0.2,
                'times': 1
            },
            'is': {
                '1': 0.1,
                '2': 0.142857,
                'times': 2
            },
            'never': {
                '3': 0.333333,
                'times': 1
            },
            'stop': {
                '3': 0.333333,
                'times': 1
            },
            'game': {
                '1': 0.2,
                'times': 1
            },
            'learning': {
                '1': 0.1,
                '3': 0.333333,
                'times': 2
            },
            'not': {
                '2': 0.142857,
                'times': 1
            },
            'the': {
                '1': 0.1,
                '2': 0.142857,
                'times': 2
            },
            'everlasting': {
                '1': 0.1,
                'times': 1
            },
            'worth': {
                '2': 0.142857,
                'times': 1
            }
        }
        expected_step_2_words_dict = {
            'a': {
                '1': 0.1,
                'idf': 2.098612289,
                'times': 1
            },
            'unexamined': {
                'idf': 2.098612289,
                '2': 0.142857,
                'times': 1
            },
            'life': {
                '1': 0.1,
                'idf': 1.405465108,
                '2': 0.142857,
                'times': 2
            },
            'living': {
                'idf': 2.098612289,
                '2': 0.142857,
                'times': 1
            },
            'of': {
                '1': 0.2,
                'idf': 2.098612289,
                'times': 1
            },
            'is': {
                '1': 0.1,
                'idf': 1.405465108,
                '2': 0.142857,
                'times': 2
            },
            'never': {
                'idf': 2.098612289,
                '3': 0.333333,
                'times': 1
            },
            'stop': {
                'idf': 2.098612289,
                '3': 0.333333,
                'times': 1
            },
            'game': {
                '1': 0.2,
                'idf': 2.098612289,
                'times': 1
            },
            'learning': {
                '1': 0.1,
                'idf': 1.405465108,
                '3': 0.333333,
                'times': 2
            },
            'not': {
                'idf': 2.098612289,
                '2': 0.142857,
                'times': 1
            },
            'the': {
                '1': 0.1,
                'idf': 1.405465108,
                '2': 0.142857,
                'times': 2
            },
            'everlasting': {
                '1': 0.1,
                'idf': 2.098612289,
                'times': 1
            },
            'worth': {
                'idf': 2.098612289,
                '2': 0.142857,
                'times': 1
            }
        }
        self.cosine.step_1()
        self.assertDictEqual(expected_step_1_words_dict, self.cosine.words_dict)

        self.cosine.step_2()
        self.assertDictEqual(expected_step_2_words_dict, self.cosine.words_dict)
        # https://janav.wordpress.com/2013/10/27/tf-idf-and-cosine-similarity/
        results_cosine = self.cosine.query_similarity_vector("life learning", 10)
        self.assertListEqual(results_cosine, [('1', '1.00000'), ('2', '0.70711'), ('3', '0.70711')])

        createFrequency.FILES_DIRECTORY = "files_eng_2"
        # https://turi.com/learn/userguide/feature-engineering/bm25.html
        self.cosine = createFrequency.CosineSimilarity()
        self.cosine.step_1()
        self.cosine.step_2()
        results_bm25 = self.cosine.bm25("a query example", 10)
        self.assertListEqual(results_bm25, [('2', 0.7896821236962175), ('1', 0.7447116155130616), ('3', 0.0)])

if __name__ == '__main__':
    unittest.main()
