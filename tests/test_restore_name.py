import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import _restore_name


def test_restore_name_is_case_insensitive():
    assert _restore_name("the client company grows", "Acme") == "Acme grows"
    assert _restore_name("The client company grows", "Acme") == "Acme grows"
    assert _restore_name("THE CLIENT COMPANY grows", "Acme") == "Acme grows"


def test_restore_name_recurses_and_survives_regex_chars():
    payload = {"a": ["The client company wins"], "b": {"c": "the client company"}, "n": 3}
    assert _restore_name(payload, r"A\B (C)") == {
        "a": [r"A\B (C) wins"],
        "b": {"c": r"A\B (C)"},
        "n": 3,
    }


if __name__ == "__main__":
    test_restore_name_is_case_insensitive()
    test_restore_name_recurses_and_survives_regex_chars()
    print("ok")
