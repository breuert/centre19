import core.data_preparation as dprep
import core.evaluation as evaluation
import core.feature_preparation as fprep
import core.prediction as pred
import core.ranking as rank
import core.tfidf_vectorization as tfidf_vec
import core.util as util
import core.training as train

from config.config import path, file

data_prep = False
robust_only = True  # train only with robust data

paths_to_check = [
    path['wapo'],
    path['robust'],
    path['union_wapo_robust'],
    path['train_feat'],
    path['tmp'],
    path['complete_run'],
    path['single_runs'],
    path['tfidf']
]


def main():
    # Setup directories
    util.check_path(paths_to_check)
    # Delete old shelve with features, if existent
    util.delete_shelve(file['feat_wapo_robust04'])

    if data_prep:
        # Extract single raw text document files from Washington Post JSON-lines file
        dprep.raw_text_from_wapo(file['wapo_jl'], path['wapo_raw'])
        dprep.clean_raw_text(path['wapo_raw'], path['wapo'], wapo=True)

        # Extract single raw text document files from TREC Disks 4 & 5
        dprep.raw_text_from_trec(path['trec45'], path['tmp'], path['robust_raw'])
        dprep.clean_raw_text(path['robust_raw'], path['robust'])

        # Make union corpus
        if not robust_only:
            corpora = [path['wapo'], path['robust']]
            dprep.unify(path['union_wapo_robust'], corpora)

    # Generate tfidf-vectorizer
    if robust_only:
        tfidf_vec.dump_tfidf_vectorizer(file['vectorizer_wapo_robust04'], path['robust'])
    else:
        tfidf_vec.dump_tfidf_vectorizer(file['vectorizer_wapo_robust04'], path['union_wapo_robust'])

    # Prepare tfidf-features
    fprep.prepare_corpus_feature(file['vectorizer_wapo_robust04'], path['wapo'], file['feat_wapo_robust04'])

    # Find intersecting topics
    qrel_files = [file['qrel_wapo'], file['qrel_robust']]
    topics = util.find_inter_top(qrel_files)

    topic_curr = 1
    if topics is not None:
        for topic in topics:
            print("Processing topic " + str(topic_curr) + " of " + str(len(topics)))

            if robust_only:
                n_feat = train.prep_train_feat(
                    file['vectorizer_wapo_robust04'],
                    file['qrel_robust'],
                    topic,
                    path['robust'],
                    path['train_feat'])
            else:
                n_feat = train.prep_train_feat(
                    file['vectorizer_wapo_robust04'],
                    file['qrel_robust'],
                    topic,
                    path['union_wapo_robust'],
                    path['train_feat'])

            model = train.train(path['train_feat'], topic, n_feat, model_type='logreg-scikit')

            pred.predict(model, file['feat_wapo_robust04'], file['score_wapo_robust04'])

            rank.rank(file['score_wapo_robust04'], topic, path['single_runs'])

            topic_curr += 1

        complete_run_file = path['complete_run'] + 'irc_task2_WCrobust04_001'
        evaluation.merge_single_topics(path['single_runs'], complete_run_file)
        evaluation.evaluate(file['trec_eval'], file['qrel_wapo'], complete_run_file)
        util.clear_path([path['single_runs'], path['train_feat']])

    else:
        print("No intersecting topics")


if __name__ == '__main__':
    main()
