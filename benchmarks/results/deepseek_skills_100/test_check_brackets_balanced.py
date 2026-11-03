import pytest
from check_brackets_balanced import check_brackets_balanced


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("", True),
        ("()", True),
        ("[]", True),
        ("{}", True),
        ("()[]{}", True),
        ("{[()]}", True),
        ("((()))", True),
        ("a(b)c[d]e{f}", True),
        ("no brackets here", True),
        ("(", False),
        (")", False),
        ("(()", False),
        ("())", False),
        ("([)]", False),
        ("{[}]", False),
        ("(]", False),
        ("[(])", False),
        ("}{}", False),
        ("(((((((((())))))))))", True),
        ("(((((((((()))))))))", False),
    ],
)
def test_check_brackets_balanced(expression, expected):
    assert check_brackets_balanced(expression) is expected


def test_returns_bool_type():
    result = check_brackets_balanced("()")
    assert isinstance(result, bool)


def test_non_string_raises_type_error():
    with pytest.raises(TypeError):
        check_brackets_balanced(123)


def test_none_raises_type_error():
    with pytest.raises(TypeError):
        check_brackets_balanced(None)
