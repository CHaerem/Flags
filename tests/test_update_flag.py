import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from types import SimpleNamespace
from scripts import update_flag


def test_update_flag_safely_no_display(monkeypatch):
    sample_country = {"name": {"common": "Norway"}}
    sample_data = {"Norway": sample_country}

    monkeypatch.setattr(update_flag, "get_country_data", lambda: sample_data)
    monkeypatch.setattr(update_flag, "get_country_by_name", lambda data, name: sample_country)
    monkeypatch.setattr(update_flag, "get_flag", lambda c: "flag_img")
    called = {"metadata": False}
    def fake_update(country):
        called["metadata"] = True
    monkeypatch.setattr(update_flag, "update_flag_metadata", fake_update)

    fake_display_manager = SimpleNamespace(
        is_display_available=lambda: False,
        display_image=lambda img: True,
    )
    monkeypatch.setattr(update_flag, "get_display_manager", lambda config=None: fake_display_manager)
    monkeypatch.setattr(update_flag, "DISPLAY_AVAILABLE", False)

    result = update_flag.update_flag_safely("Norway")
    assert result == 0
    assert called["metadata"]
