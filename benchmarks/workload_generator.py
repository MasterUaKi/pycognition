# Version: 0.1.0 | Release Date: 2026-11-03
"""
Генератор нагрузочного профиля из 100 сложных гетерогенных задач
для экспериментальной валидации фреймворка pycognition.
"""

import random
from typing import Any, Dict, List


def generate_complex_100_workload(seed: int = 42) -> List[Dict[str, Any]]:
    """
    Генерирует 100 задач: 85 алгоритмических (по закону Ципфа на базе 12 классов)
    и 15 открытых аналитических запросов для Системы 2.
    """
    random.seed(seed)
    tasks: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. ШАБЛОНЫ СЛОЖНЫХ АЛГОРИТМИЧЕСКИХ ЗАДАЧ (СИСТЕМА 1 / КРИСТАЛЛИЗАЦИЯ)
    # -------------------------------------------------------------

    # Шаблон 1: Расчет расстояния по формуле гаверсинусов (Haversine distance)
    haversine_prompts = [
        "calculate haversine distance between two coordinates in km",
        "compute great circle distance between lat lon coordinates in kilometers",
        "calculate haversine distance between two coordinates in km",
    ]
    coords_pool = [
        {"lat1": 52.756, "lon1": 8.289, "lat2": 53.079, "lon2": 8.801},  # Vechta -> Bremen
        {"lat1": 52.520, "lon1": 13.405, "lat2": 48.135, "lon2": 11.582}, # Berlin -> Munich
        {"lat1": 50.110, "lon1": 8.682, "lat2": 53.551, "lon2": 9.993},   # Frankfurt -> Hamburg
        {"lat1": 51.507, "lon1": -0.127, "lat2": 48.856, "lon2": 2.352},  # London -> Paris
    ]

    # Шаблон 2: Расстояние Левенштейна (Levenshtein edit distance)
    levenshtein_prompts = [
        "compute levenshtein distance between two strings",
        "calculate minimum edit distance between word a and word b",
        "compute levenshtein distance between two strings",
    ]
    strings_pool = [
        {"s1": "algorithm", "s2": "altruistic"},
        {"s1": "pycognition", "s2": "cognition"},
        {"s1": "metacognition", "s2": "arbitration"},
        {"s1": "crystallizer", "s2": "crystal"},
    ]

    # Шаблон 3: Агрегация транзакций по категориям (Data aggregation)
    agg_prompts = [
        "aggregate transaction amounts by category and return dictionary",
        "sum total amounts per category from transaction records",
    ]
    transactions_pool = [
        {"records": [{"category": "groceries", "amount": 45.2}, {"category": "utilities", "amount": 120.0}, {"category": "groceries", "amount": 18.5}]},
        {"records": [{"category": "servers", "amount": 350.0}, {"category": "licenses", "amount": 1200.0}, {"category": "servers", "amount": 85.0}]},
        {"records": [{"category": "books", "amount": 25.0}, {"category": "travel", "amount": 180.0}, {"category": "books", "amount": 45.0}]},
    ]

    # Шаблон 4: Извлечение IPv4-адресов из текста (Log / String parsing)
    ip_prompts = [
        "extract all valid ipv4 addresses from unstructured text into list",
        "parse valid ipv4 addresses from log message string",
    ]
    ip_logs_pool = [
        {"text": "Failed login from 192.168.1.45 at port 22 and redirect to 10.0.0.1"},
        {"text": "Ping statistics for 172.16.254.1: packets sent 4, host 8.8.8.8 active"},
        {"text": "Cluster nodes: 10.10.1.15, backup node 192.168.0.254 online"},
    ]

    # Шаблон 5: Аннуитетный платеж по кредиту (Financial amortization)
    loan_prompts = [
        "calculate monthly annuity loan payment and total interest paid",
        "compute monthly payment for loan given principal annual rate and months",
    ]
    loans_pool = [
        {"principal": 250000.0, "annual_rate": 0.035, "tenure_months": 240},
        {"principal": 50000.0, "annual_rate": 0.048, "tenure_months": 60},
        {"principal": 12000.0, "annual_rate": 0.065, "tenure_months": 36},
    ]

    # Шаблон 6: Выявление выбросов по Z-score (Statistical anomaly detection)
    zscore_prompts = [
        "detect outlier indices from numeric list using z score threshold",
        "find outlier positions in numeric array where absolute z score exceeds threshold",
    ]
    zscore_pool = [
        {"values": [10.0, 12.0, 11.5, 9.8, 10.2, 85.0, 11.1, 10.5], "threshold": 2.0},
        {"values": [100.0, 102.0, 98.0, 101.0, 550.0, 99.0, 103.0], "threshold": 2.2},
        {"values": [1.2, 1.4, 1.1, 1.3, -8.5, 1.5, 1.2], "threshold": 2.0},
    ]

    # Шаблон 7: Экспоненциальное скользящее среднее (EMA)
    ema_prompts = [
        "calculate exponential moving average series for numeric values",
        "compute ema array from numeric values with given alpha smoothing factor",
    ]
    ema_pool = [
        {"values": [10.0, 11.0, 12.0, 11.5, 13.0, 14.2, 15.0], "alpha": 0.3},
        {"values": [100.0, 95.0, 92.0, 96.0, 98.0, 102.0], "alpha": 0.2},
    ]

    # Шаблон 8: Проверка валидности скобочной последовательности (Syntax check)
    brackets_prompts = [
        "validate if bracket sequence string is balanced and properly nested",
        "check if brackets parentheses and curly braces are balanced",
    ]
    brackets_pool = [
        {"expression": "{[()()]}"},
        {"expression": "{[(])}"},
        {"expression": "def foo(): return (data[idx] + {k: v})"},
    ]

    # Шаблон 9: Подсчет частоты слов за вычетом стоп-слов (NLP Token statistics)
    nlp_prompts = [
        "count top word frequencies in text excluding common english stop words",
        "compute word frequency dictionary from text filtering out stop words",
    ]
    nlp_pool = [
        {"text": "cognitive architecture uses procedural memory and working memory for cognitive tasks", "top_k": 3},
        {"text": "dual process theory explains system one fast thinking and system two slow deliberation", "top_k": 4},
    ]

    # Шаблон 10: Умножение матриц и вычисление следа (Linear algebra)
    matrix_prompts = [
        "multiply two square matrices and calculate trace of result matrix",
        "compute matrix multiplication product and trace",
    ]
    matrix_pool = [
        {"matrix_a": [[1.0, 2.0], [3.0, 4.0]], "matrix_b": [[5.0, 6.0], [7.0, 8.0]]},
        {"matrix_a": [[2.0, 0.0], [1.0, 3.0]], "matrix_b": [[1.0, 2.0], [3.0, 1.0]]},
    ]

    # Шаблон 11: RLE-сжатие строк (Run-length encoding)
    rle_prompts = [
        "encode string using run length encoding format",
        "compress string using run length encoding",
    ]
    rle_pool = [
        {"input_str": "WWWWWWAAAAAABBBBCCCCCDDD"},
        {"input_str": "AABBBCCCCCDDDEEEEFFFFF"},
    ]

    # Шаблон 12: Расчет рабочих дней между двумя датами (ISO dates)
    date_prompts = [
        "calculate count of business weekdays between two iso date strings",
        "count working days excluding weekends between start date and end date",
    ]
    date_pool = [
        {"start_date": "2026-11-01", "end_date": "2026-11-20"},
        {"start_date": "2026-12-15", "end_date": "2027-01-15"},
    ]

    # Список пулов генерации алгоритмических задач
    algorithmic_generators = [
        (haversine_prompts, coords_pool, 12),    # 12 вызовов
        (levenshtein_prompts, strings_pool, 10), # 10 вызовов
        (agg_prompts, transactions_pool, 9),     # 9 вызовов
        (ip_prompts, ip_logs_pool, 8),           # 8 вызовов
        (loan_prompts, loans_pool, 8),           # 8 вызовов
        (zscore_prompts, zscore_pool, 7),        # 7 вызовов
        (ema_prompts, ema_pool, 7),              # 7 вызовов
        (brackets_prompts, brackets_pool, 6),    # 6 вызовов
        (nlp_prompts, nlp_pool, 6),              # 6 вызовов
        (matrix_prompts, matrix_pool, 4),        # 4 вызова
        (rle_prompts, rle_pool, 4),              # 4 вызова
        (date_prompts, date_pool, 4),            # 4 вызова
    ]

    # Наполняем алгоритмические задачи (всего 85 штук)
    algo_tasks = []
    for prompts, pool, count in algorithmic_generators:
        for _ in range(count):
            p = random.choice(prompts)
            payload = random.choice(pool).copy()
            algo_tasks.append({"prompt": p, "payload": payload, "is_deliberative": False})

    # -------------------------------------------------------------
    # 2. ОТКРЫТЫЕ АНАЛИТИЧЕСКИЕ ЗАДАЧИ ДЛЯ СИСТЕМЫ 2 (15 ШТУК)
    # -------------------------------------------------------------
    conceptual_prompts = [
        "Analyze the architectural trade-offs between amortized procedural execution and continuous frontier LLM prompting.",
        "Compare dual-process cognitive theories in neurobiology with multi-agent orchestration frameworks.",
        "Evaluate the security risks of Abstract Syntax Tree inspection versus hardware-level virtualization sandboxes.",
        "Discuss methods to eliminate catastrophic forgetting in continual learning for agent memory stores.",
        "How can meta-cognitive arbitration thresholds be dynamically adapted using contextual multi-armed bandits?",
        "Assess the impact of quadratic attention complexity on autonomous agents with long interaction histories.",
        "Explain how DSpace-CRIS models research entities using the KDSF 2.1 standard for academic repositories.",
        "Propose a formal verification protocol for LLM-synthesized unit test suites.",
        "Analyze latency distribution tails in high-throughput enterprise agent middleware.",
        "Explain the theoretical limits of code synthesis when reducing non-deterministic natural language intents.",
        "Compare optimistic vs pessimistic concurrency control in distributed vector stores.",
        "How can zero-downtime hot-reloading of Python modules be safeguarded in multi-threaded runtimes?",
        "Discuss inductive biases of transformer architectures when handling arithmetic reasoning.",
        "Analyze the cost-utility Pareto frontier for hybrid neurosymbolic architectures.",
        "Evaluate the trade-offs of using LGPL-3.0-or-later licensing for institutional scientific software tooling.",
    ]

    conceptual_tasks = [
        {"prompt": prompt, "payload": {}, "is_deliberative": True}
        for prompt in conceptual_prompts
    ]

    # Объединяем и перемешиваем задачи, гарантируя, что первичные вызовы классов
    # распределены равномерно по выборке
    random.shuffle(algo_tasks)

    # Вставляем концептуальные задачи равномерно каждые ~6-7 шагов
    combined_tasks: List[Dict[str, Any]] = []
    algo_idx = 0
    conc_idx = 0

    for i in range(100):
        if (i % 7 == 3 or algo_idx >= len(algo_tasks)) and conc_idx < len(conceptual_tasks):
            combined_tasks.append(conceptual_tasks[conc_idx])
            conc_idx += 1
        else:
            combined_tasks.append(algo_tasks[algo_idx])
            algo_idx += 1

    return combined_tasks
