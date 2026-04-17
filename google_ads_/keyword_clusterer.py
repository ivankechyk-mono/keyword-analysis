from config import BRAND_VARIATIONS, PRODUCT_KEYWORDS


def classify_keyword(keyword: str) -> dict:
    """
    Детерміновано класифікує ключове слово по бренду та продукту.
    Повертає: {is_brand, product, matched_trigger}
    """
    kw = keyword.lower()

    is_brand = any(brand.lower() in kw for brand in BRAND_VARIATIONS)

    matched_product = None
    matched_trigger = None
    for product, triggers in PRODUCT_KEYWORDS.items():
        for trigger in triggers:
            if trigger.lower() in kw:
                matched_product = product
                matched_trigger = trigger
                break
        if matched_product:
            break

    return {
        "keyword": keyword,
        "is_brand": is_brand,
        "product": matched_product,
        "matched_trigger": matched_trigger,
    }


def cluster_keywords(keywords: list[dict]) -> dict[str, list[dict]]:
    """
    Приймає список {keyword, avg_monthly_searches, ...}
    Повертає згруповані кластери.
    """
    clusters = {
        "brand_only": [],
        "brand_product": [],
        "product_only": [],
        "generic": [],
    }

    for item in keywords:
        classification = classify_keyword(item["keyword"])
        item.update(classification)

        if classification["is_brand"] and classification["product"]:
            clusters["brand_product"].append(item)
        elif classification["is_brand"]:
            clusters["brand_only"].append(item)
        elif classification["product"]:
            clusters["product_only"].append(item)
        else:
            clusters["generic"].append(item)

    return clusters


def cluster_all(data: dict) -> dict:
    """
    Приймає результат collect_all() і кластеризує всі ключові слова.
    """
    all_keywords = []
    for product_keywords in data.get("products", {}).values():
        all_keywords.extend(product_keywords)

    # Дедублікація по keyword
    seen = set()
    unique = []
    for kw in all_keywords:
        if kw["keyword"] not in seen:
            seen.add(kw["keyword"])
            unique.append(kw)

    return cluster_keywords(unique)


if __name__ == "__main__":
    import json
    from google_ads_.keyword_collector import collect_all
    data = collect_all()
    clusters = cluster_all(data)
    for cluster_name, items in clusters.items():
        print(f"\n{cluster_name}: {len(items)} keywords")
        for item in items[:3]:
            print(f"  {item['keyword']} — {item['avg_monthly_searches']} searches/mo")
