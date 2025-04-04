import time
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer

from core.util import directory_list


def _stemming(str_input):
    stemmer = PorterStemmer()
    # stemmer = SnowballStemmer('english')
    words = re.sub(r"[^A-Za-z0-9\-]", " ", str_input).lower().split()
    words = [stemmer.stem(word) for word in words]
    return words


def dump_tfidf_vectorizer(vectorizer_pick, union):
    '''Use this function to pickle a vectorizer object. The tfidf-vectorizer object will be made from
    files of a specified directory.
    :param vectorizer_pick: path to file where pickled vectorizer will be written
    :param union: path to directory of union corpus
    :return: -
    '''

    print('Dumping tfidf-vectorizer')
    union_list = directory_list(union)

    # set min_df to 0.2 in order to prevent memory errors, default val = 1.0
    # handing over a tokenizer will result in long processing times, better perform stemming with
    # an extra script/function
    # vectorizer = TfidfVectorizer(input='filename', stop_words='english', min_df=0.25, tokenizer=_stemming)
    vectorizer = TfidfVectorizer(input='filename')
    start_time = time.time()
    vectorizer.fit(union_list)  # making this matrix will take approx. 9-10 min with 1m docs (i7 CPU)
    print("Time needed for making tfidf-matrix: ", str(time.time() - start_time))

    with open(vectorizer_pick, 'wb') as dump:
        pickle.dump(vectorizer, dump)

    # joblib.dump(vectorizer, 'tfidfvectorizer.sav')  # joblib is an alternative to pickle


def load_vectorizer(vectorizer_pick):
    '''Use this function to load a vectorizer object from a pickle file.
    :param vectorizer_pick: path to file where tfidf-vectorizer are dumped
    :return: -
    '''
    print('Loading tfidf-vectorizer...')
    vectorizer_file = open(vectorizer_pick, 'rb')
    vectorizer = pickle.load(vectorizer_file)
    # vectorizer = joblib.load('tfidfvectorizer.sav')  # joblib is an alternative to pickle

    return vectorizer
