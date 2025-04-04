import core.data_preparation as dprep
import core.evaluation as evaluation
import core.feature_preparation as fprep
import core.prediction as pred
import core.ranking as rank
import core.tfidf_vectorization as tfidf_vec
import core.util as util
import core.training as train

from config.config import path, file

data_prep = True
robust_only = True

paths_to_check = [
    path['wapo'],
    path['robust'],
    path['aquaint'],
    path['union_wapo_robust_aquaint'],
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
    util.delete_shelve(file['feat_wapo_robust0405'])

    if data_prep:
        # Extract single raw text document files from Washington Post JSON-lines file
        dprep.raw_text_from_wapo(file['wapo_jl'], path['wapo_raw'])
        dprep.clean_raw_text(path['wapo_raw'], path['wapo'], wapo=True)

        # Extract single raw text document files from TREC Disks 4 & 5
        dprep.raw_text_from_trec(path['trec45'], path['tmp'], path['robust_raw'])
        dprep.clean_raw_text(path['robust_raw'], path['robust'])

        # Extract single raw text document files from AQUAINT corpus
        dprep.raw_text_from_trec(path['aquaint_compr'], path['tmp'], path['aquaint_raw'])
        dprep.clean_raw_text(path['aquaint_raw'], path['aquaint'])

        # Make union corpus
        if robust_only:
            corpora = [path['robust'], path['aquaint']]
            dprep.unify(path['union_robust_aquaint'], corpora)

        else:
            corpora = [path['wapo'], path['robust'], path['aquaint']]
            dprep.unify(path['union_wapo_robust_aquaint'], corpora)

    # Generate tfidf-vectorizer
    if robust_only:
        tfidf_vec.dump_tfidf_vectorizer(file['vectorizer_wapo_robust0405'], path['union_robust_aquaint'])
    else:
        tfidf_vec.dump_tfidf_vectorizer(file['vectorizer_wapo_robust0405'], path['union_wapo_robust_aquaint'])

    # Prepare tfidf-features
    fprep.prepare_corpus_feature(file['vectorizer_wapo_robust0405'], path['wapo'], file['feat_wapo_robust0405'])

    # Find intersecting topics
    qrel_files = [file['qrel_wapo'], file['qrel_robust'], file['qrel_aquaint']]
    topics = util.find_inter_top(qrel_files)

    # Merge qrel files from Robust04 and Robust05
    util.merge_qrels(qrel_files[1:], file['qrel_robust_aquaint'])

    topic_curr = 1
    if topics is not None:
        for topic in topics:
            print("Processing topic " + str(topic_curr) + " of " + str(len(topics)))

            if robust_only:
                n_feat = train.prep_train_feat(
                    file['vectorizer_wapo_robust0405'],
                    file['qrel_robust_aquaint'],
                    topic,
                    path['union_robust_aquaint'],
                    path['train_feat'])
            else:
                n_feat = train.prep_train_feat(
                    file['vectorizer_wapo_robust0405'],
                    file['qrel_robust_aquaint'],
                    topic,
                    path['union_wapo_robust_aquaint'],
                    path['train_feat'])

            model = train.train(path['train_feat'], topic, n_feat, model_type='logreg-scikit')

            pred.predict(model, file['feat_wapo_robust0405'], file['score_wapo_robust0405'])

            rank.rank(file['score_wapo_robust0405'], topic, path['single_runs'])

            topic_curr += 1

        complete_run_file = path['complete_run'] + 'irc_task2_WCrobust0405_001'
        evaluation.merge_single_topics(path['single_runs'], complete_run_file)
        evaluation.evaluate(file['trec_eval'], file['qrel_wapo'], complete_run_file)
        util.clear_path([path['single_runs'], path['train_feat']])

    else:
        print("No intersecting topics")


if __name__ == '__main__':
    main()
