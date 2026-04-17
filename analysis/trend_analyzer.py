from collections import defaultdict


MONTH_NAMES = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень",
}


def build_monthly_timeline(keywords: list[dict]) -> dict[str, list[dict]]:
    """
    Будує помісячну динаміку для кожного ключового слова.
    Повертає: {keyword: [{year, month, searches}, ...]}
    """
    timeline = {}
    for kw in keywords:
        monthly = sorted(
            kw.get("monthly_searches", []),
            key=lambda x: (x["year"], x["month"])
        )
        timeline[kw["keyword"]] = monthly
    return timeline


def aggregate_by_month(keywords: list[dict]) -> list[dict]:
    """
    Агрегує сумарні пошуки по місяцях по всіх ключових словах.
    """
    totals = defaultdict(int)
    for kw in keywords:
        for month in kw.get("monthly_searches", []):
            key = (month["year"], month["month"])
            totals[key] += month["searches"]

    return [
        {
            "year": year,
            "month": month,
            "month_name": MONTH_NAMES.get(month, str(month)),
            "total_searches": searches,
        }
        for (year, month), searches in sorted(totals.items())
    ]


def calculate_growth(timeline: list[dict]) -> dict:
    """
    Розраховує зростання між останніми двома місяцями.
    """
    if len(timeline) < 2:
        return {"growth_abs": 0, "growth_pct": 0}

    prev = timeline[-2]["total_searches"]
    curr = timeline[-1]["total_searches"]
    growth_abs = curr - prev
    growth_pct = round((growth_abs / prev * 100), 1) if prev > 0 else 0

    return {
        "prev_month": f"{MONTH_NAMES.get(timeline[-2]['month'])} {timeline[-2]['year']}",
        "curr_month": f"{MONTH_NAMES.get(timeline[-1]['month'])} {timeline[-1]['year']}",
        "prev_searches": prev,
        "curr_searches": curr,
        "growth_abs": growth_abs,
        "growth_pct": growth_pct,
        "direction": "↑" if growth_abs > 0 else "↓" if growth_abs < 0 else "→",
    }


def detect_seasonality(timeline: list[dict]) -> dict[int, float]:
    """
    Розраховує сезонний індекс по місяцях (середній місяць = 1.0).
    """
    by_month = defaultdict(list)
    for entry in timeline:
        by_month[entry["month"]].append(entry["total_searches"])

    avg_by_month = {m: sum(v) / len(v) for m, v in by_month.items()}
    overall_avg = sum(avg_by_month.values()) / len(avg_by_month) if avg_by_month else 1

    return {
        m: round(avg / overall_avg, 2)
        for m, avg in avg_by_month.items()
    }


def analyze(data: dict) -> dict:
    """
    Головна функція. Приймає результат collect_all() і повертає повний аналіз.
    """
    all_keywords = []
    for kw_list in data.get("products", {}).values():
        all_keywords.extend(kw_list)

    timeline = aggregate_by_month(all_keywords)
    growth = calculate_growth(timeline)
    seasonality = detect_seasonality(timeline)

    product_summaries = {}
    for product, kw_list in data.get("products", {}).items():
        product_timeline = aggregate_by_month(kw_list)
        product_summaries[product] = {
            "timeline": product_timeline,
            "growth": calculate_growth(product_timeline),
        }

    return {
        "overall_timeline": timeline,
        "overall_growth": growth,
        "seasonality": seasonality,
        "by_product": product_summaries,
    }


if __name__ == "__main__":
    import json
    from google_ads_.keyword_collector import collect_all
    data = collect_all()
    result = analyze(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
