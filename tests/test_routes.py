import sys
import types; sys.modules["sounddevice"] = types.ModuleType("sounddevice"); sys.modules["vosk"] = types.ModuleType("vosk"); sys.modules["vosk"].Model = object; sys.modules["vosk"].KaldiRecognizer = object
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from app.routes import match_country


def test_match_country_exact():
    assert match_country('Japan') == 'Japan'


def test_match_country_alternative():
    assert match_country('change to usa') == 'United States'


def test_match_country_not_found():
    assert match_country('I love Mars') is None
