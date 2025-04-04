import time
import shelve

from tqdm import tqdm
from sklearn.linear_model import LogisticRegression


def predict(model, corpus_feat, corpus_score):
    '''Use this function to predict the tfidf-features from a corpus.
    :param model: the previously trained logistic regression model
    :param corpus_feat: the tfidf-features of a corpus stored in a shelve
    :param corpus_score: path to directory where scores of a topic run will be written
    :return: -
    '''
    print('Perform predictions on corpus...')
    start_time = time.time()

    id_and_tfidf = shelve.open(corpus_feat)

    file = open(corpus_score, 'w')

    t = tqdm(total=len(id_and_tfidf.keys()))

    for key in id_and_tfidf:
        doc_tfidf = id_and_tfidf[key]
        score = model.predict_proba(doc_tfidf)[0][1]
        file.write(key + " " + str(score) + "\n")
        t.update()

    t.close()
    id_and_tfidf.close()
    file.close()
    print("Predictions on corpus took ", str(time.time() - start_time), ' seconds.')