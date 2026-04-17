import json
from datetime import datetime, timezone
from pathlib import Path

from google_ads_.keyword_collector import collect_all
from google_ads_.keyword_clusterer import cluster_all
from analysis.trend_analyzer import analyze
from analysis.ai_analyst import run_full_analysis

DATA_FILE = Path(__file__).parent / "data" / "dashboard_data.json"


def main():
    print("1. Збір даних з Google Ads Keyword Planner...")
    raw_data = collect_all()

    print("2. Кластеризація ключових слів...")
    clusters = cluster_all(raw_data)
    for name, items in clusters.items():
        print(f"   {name}: {len(items)} keywords")

    print("3. Аналіз трендів...")
    analysis = analyze(raw_data)
    growth = analysis["overall_growth"]
    print(f"   {growth.get('prev_month')} → {growth.get('curr_month')}: "
          f"{growth.get('growth_pct'):+.1f}% {growth.get('direction')}")

    print("4. Генерація AI інсайтів...")
    ai_result = run_full_analysis(analysis)
    print(f"\n  {ai_result['insights']}\n")

    print("5. Збереження даних для веб-дашборду...")
    DATA_FILE.parent.mkdir(exist_ok=True)
    dashboard_payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "overall_timeline": analysis["overall_timeline"],
        "by_product": {
            product: {
                "timeline": summary["timeline"],
                "growth": summary["growth"],
            }
            for product, summary in analysis["by_product"].items()
        },
        "summary": ai_result["looker"]["summary"],
        "insights": ai_result["insights"],
        "seasonality": analysis["seasonality"],
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dashboard_payload, f, ensure_ascii=False, indent=2)
    print(f"   Збережено у {DATA_FILE}")

    print("\nГотово. Відкрий http://localhost:8000 щоб переглянути дашборд.")


if __name__ == "__main__":
    main()
