def test_embedding_import():
    from ml.embeddings import get_model
    assert callable(get_model)
