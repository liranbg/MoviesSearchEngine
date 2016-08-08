# encoding:utf-8
import urllib
import string
import re
from bgutags_new import *

def call_meni(text):
    text_encoded = text.encode('utf-8')
    params = urllib.urlencode({'text': text_encoded})
    didnt_got_tags = True
    while didnt_got_tags:
        try:
            f = urllib.urlopen("HTTP://127.0.0.1:8086/bm", params)
            words = f.readlines()
            for word in words:
                if 'http error' in word.lower():
                    print 'error'
                    continue
            didnt_got_tags = False
        except:
            print 'meni error ???!?!'
    lemmas = []
    for word in words:
        if not word == '\n' and not word == '\r\n':
            splt = word.split('\t')
            lemmatized = splt
            pos = tostring1(int(splt[1])).split(',')[0].split(':')[1].split('-')[0]
            lemmas.append((splt[0], lemmatized, pos))
    return lemmas




#texxt = "אני חולמת ועושה תכניות כאילו לא אירע כלום בעולם;  כאילו אין מלחמה והרס, אין אלפי מתים יום יום, אין מטוסים ומפציצים, וגרמניה, אנגליה, איטליה ויוון אינן משמידות זו את זו.  רק בארץ-ישראל הקטנה שלנו, שאף היא נתונה בסכנה ושעתידה אולי להימצא במרכז חזית המלחמה – בה כאילו שקט ושלווה.  ואני יושבת בתוכה וחושבת על העתיד.  ומה אני חושבת על העתיד הפרטי שלי?  – אחת התכניות היפות:  להיות מדריכה ללול במושבים, לנסוע ממקום למקום, לעבור במשקים, לייעץ ולעזור, לארגן, להנהיג רישום, לפתח את הענף.  בערב לתת סמינריון קצר לאנשי המושב וללמדם את הדברים החשובים בענף.  ודרך אגב, להכיר את האנשים, את חייהם, להסתובב קצת בארץ."


def run_meni(texxt):
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in texxt if ch not in exclude)
    lemmas = call_meni(s)
    return [word[1][2] for word in lemmas]


#run_meni(texxt)