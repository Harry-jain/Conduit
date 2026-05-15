from src.enrollment.sentence_corpus import SentenceCorpus


def test_sentence_corpus_size_and_length() -> None:
    corpus = SentenceCorpus()
    assert len(corpus.get_all()) == 60
    assert all(len(s.split()) >= 15 for s in corpus.get_all())
