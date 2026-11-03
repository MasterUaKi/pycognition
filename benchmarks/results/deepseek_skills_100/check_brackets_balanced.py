def check_brackets_balanced(expression: str) -> bool:
    """Проверяет сбалансированность круглых, квадратных и фигурных скобок.

    Возвращает True, если все скобки сбалансированы с учётом вложенности,
    иначе False. Не-скобочные символы игнорируются.
    """
    if not isinstance(expression, str):
        raise TypeError("expression must be a str")

    pairs = {')': '(', ']': '[', '}': '{'}
    opening = set(pairs.values())
    stack = []

    for ch in expression:
        if ch in opening:
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()

    return not stack
