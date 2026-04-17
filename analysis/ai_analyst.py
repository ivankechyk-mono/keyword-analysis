import requests
from config import PRODUCT_KEYWORDS, ENOT_API_KEY, ENOT_API_URL


MONTH_NAMES_UA = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень",
}


def _format_trend_for_prompt(analysis: dict) -> str:
    growth = analysis["overall_growth"]
    lines = [
        f"Загальна динаміка пошуків:",
        f"  {growth.get('prev_month', '—')}: {growth.get('prev_searches', 0):,} пошуків",
        f"  {growth.get('curr_month', '—')}: {growth.get('curr_searches', 0):,} пошуків",
        f"  Зміна: {growth.get('growth_abs', 0):+,} ({growth.get('growth_pct', 0):+.1f}%) {growth.get('direction', '')}",
        "",
        "По продуктах:",
    ]
    for product, summary in analysis.get("by_product", {}).items():
        g = summary["growth"]
        lines.append(
            f"  {product}: {g.get('prev_searches', 0):,} → {g.get('curr_searches', 0):,} "
            f"({g.get('growth_pct', 0):+.1f}%) {g.get('direction', '')}"
        )

    seasonality = analysis.get("seasonality", {})
    if seasonality:
        peak_month = max(seasonality, key=seasonality.get)
        lines.append(f"\nПіковий місяць: {MONTH_NAMES_UA.get(peak_month, peak_month)} (індекс {seasonality[peak_month]})")

    return "\n".join(lines)


def generate_insights(analysis: dict) -> str:
    trend_text = _format_trend_for_prompt(analysis)

    system_prompt = "Ти аналітик digital-маркетингу для Monobank (українського необанку). Відповідай українською мовою, стисло і конкретно."

    user_input = f"""Дані по пошуковим запитам у Google Ads за останні місяці:

{trend_text}

Продукти що відстежуються: {', '.join(PRODUCT_KEYWORDS.keys())}

Надай короткий аналіз (3-5 речень):
1. Що відбувається із попитом загалом
2. Які продукти ростуть / падають
3. Конкретна рекомендація для рекламних компаній"""

    schema = '{"type":"object","properties":{"insights":{"type":"string"}},"required":["insights"]}'

    response = requests.post(
        ENOT_API_URL,
        headers={"X-API-Key": ENOT_API_KEY},
        data={
            "prompt": system_prompt,
            "user_input": user_input,
            "schema": schema,
            "temperature": "0.3",
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["result"]["insights"]


def generate_looker_data(analysis: dict) -> dict:
    """
    Формує структуру даних для Looker Studio дашборду.
    """
    rows = []
    for entry in analysis.get("overall_timeline", []):
        rows.append({
            "date": f"{entry['year']}-{str(entry['month']).zfill(2)}-01",
            "product": "all",
            "searches": entry["total_searches"],
            "month_name": entry["month_name"],
        })

    for product, summary in analysis.get("by_product", {}).items():
        for entry in summary.get("timeline", []):
            rows.append({
                "date": f"{entry['year']}-{str(entry['month']).zfill(2)}-01",
                "product": product,
                "searches": entry["total_searches"],
                "month_name": entry["month_name"],
            })

    growth = analysis.get("overall_growth", {})
    return {
        "dashboard_rows": rows,
        "summary": {
            "prev_month": growth.get("prev_month"),
            "curr_month": growth.get("curr_month"),
            "growth_pct": growth.get("growth_pct"),
            "direction": growth.get("direction"),
        },
    }


def run_full_analysis(analysis: dict) -> dict:
    insights = generate_insights(analysis)
    looker_data = generate_looker_data(analysis)
    return {
        "insights": insights,
        "looker": looker_data,
    }


if __name__ == "__main__":
    import json
    from google_ads_.keyword_collector import collect_all
    from analysis.trend_analyzer import analyze

    data = collect_all()
    analysis = analyze(data)
    result = run_full_analysis(analysis)
    print("\n=== AI INSIGHTS ===")
    print(result["insights"])
    print("\n=== LOOKER DATA (перші 5 рядків) ===")
    print(json.dumps(result["looker"]["dashboard_rows"][:5], ensure_ascii=False, indent=2))
