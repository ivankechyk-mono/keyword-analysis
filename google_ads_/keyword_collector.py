from datetime import date
from google.ads.googleads.errors import GoogleAdsException
from google_ads_.google_ads_client import get_client, get_customer_id
from config import BRAND_VARIATIONS, PRODUCT_KEYWORDS


def get_keyword_ideas(keywords: list[str]) -> list[dict]:
    """
    Отримує ідеї ключових слів з Keyword Planner.
    Максимум 20 keywords за запит.
    """
    client = get_client()
    customer_id = get_customer_id()
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    # resource names для мови та гео
    request.language = client.get_service("GoogleAdsService").language_constant_path("1036")  # Ukrainian
    request.geo_target_constants.append(
        client.get_service("GoogleAdsService").geo_target_constant_path("2804")  # Ukraine
    )
    request.include_adult_keywords = False
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    request.keyword_seed.keywords.extend(keywords[:20])

    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        results = []
        for idea in response:
            monthly_searches = []
            for month in idea.keyword_idea_metrics.monthly_search_volumes:
                monthly_searches.append({
                    "year": int(month.year),
                    "month": int(month.month) - 1,  # MonthOfYear enum: JANUARY=2..DECEMBER=13, subtract 1 to get 1..12
                    "searches": int(month.monthly_searches),
                })
            results.append({
                "keyword": idea.text,
                "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
                "competition": idea.keyword_idea_metrics.competition.name,
                "monthly_searches": monthly_searches,
            })
        return results
    except GoogleAdsException as e:
        print(f"Google Ads API error: {e.error.code().name}")
        for error in e.failure.errors:
            print(f"  {error.message}")
        return []


def build_seeds(product: str) -> list[str]:
    """
    Повертає унікальні seed-слова: тригери продукту + бренд-комбінації (перші 2 бренди).
    Залишаємось в межах 20 слів, щоб вкластись в один запит.
    """
    triggers = PRODUCT_KEYWORDS[product]
    seeds = list(triggers)  # самі тригери
    # додаємо кілька бренд+тригер комбінацій для контексту
    for brand in BRAND_VARIATIONS[:2]:
        for trigger in triggers[:3]:
            seeds.append(f"{brand} {trigger}")
    return seeds[:20]


def collect_product_keywords() -> dict[str, list[dict]]:
    results = {}
    for product in PRODUCT_KEYWORDS:
        seeds = build_seeds(product)
        print(f"  [{product}] seeds ({len(seeds)}): {seeds[:3]}...")
        results[product] = get_keyword_ideas(seeds)
    return results


def collect_all() -> dict:
    return {
        "products": collect_product_keywords(),
        "collected_at": date.today().isoformat(),
    }


if __name__ == "__main__":
    import json
    data = collect_all()
    print(json.dumps(data, ensure_ascii=False, indent=2))
