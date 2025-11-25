import importlib

from app import database


def test_get_db_generator_closes_session():
    gen = database.get_db()
    db = next(gen)
    assert db is not None
    # closing the generator will execute the finally block and close the session
    gen.close()


def test_main_handles_create_all_exception(monkeypatch):
    # force Base.metadata.create_all to raise during import of app.main
    import app as app_pkg

    # replace create_all with one that raises
    orig = app_pkg.database.Base.metadata.create_all

    def _raise(*args, **kwargs):
        raise RuntimeError("no db")

    app_pkg.database.Base.metadata.create_all = _raise

    try:
        # reload main module to trigger the guarded create_all
        importlib.reload(importlib.import_module("app.main"))
    finally:
        # restore
        app_pkg.database.Base.metadata.create_all = orig
        importlib.reload(importlib.import_module("app.main"))
