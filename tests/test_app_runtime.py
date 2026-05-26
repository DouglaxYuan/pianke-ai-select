import os

import app as app_module


def test_app_main_sets_runtime_env(monkeypatch):
    called = {}

    monkeypatch.setattr(app_module, "setup_logger", lambda folder=None: None)
    monkeypatch.setattr(app_module.threading, "Timer", lambda *args, **kwargs: type("T", (), {"start": lambda self: None})())
    monkeypatch.setattr(app_module.app, "run", lambda **kwargs: called.update(kwargs))
    monkeypatch.setattr(app_module, "SCRIPT_TOKEN", None)
    monkeypatch.setattr(app_module.sys, "argv", ["app.py", "--runtime", "cpu", "--port", "6060", "--no-browser"])

    app_module.main()

    assert os.environ["PIC_SELECTER_RUNTIME"] == "cpu"
    assert called["port"] == 6060


def test_apply_runtime_selection_resets_cached_device(monkeypatch):
    from pic_selecter import vision
    vision._DEVICE = "sentinel"
    monkeypatch.setenv("PIC_SELECTER_RUNTIME", "auto")

    app_module._apply_runtime_selection("cpu")

    assert os.environ["PIC_SELECTER_RUNTIME"] == "cpu"
    assert vision._DEVICE is None
