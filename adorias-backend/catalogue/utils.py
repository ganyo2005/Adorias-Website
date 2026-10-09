"""Bridges the Django Product model back to the exact camelCase dict shape
the ported Efia engine (efia/engine.py) expects, since that engine was
transliterated directly from JS code written against window.ADORIAS_CATALOGUE
objects such as {name, keySpecifications, originalCategory, ...}.
"""
from .models import Product


def product_to_dict(p):
    d = {
        "sku": p.sku,
        "brand": p.brand,
        "name": p.name,
        "category": p.category,
        "originalCategory": p.original_category,
        "model": p.model,
        "specs": p.specs,
        "keySpecifications": p.key_specifications,
        "description": p.description,
        "compatibility": p.compatibility,
        "useCases": p.use_cases,
        "battery": p.battery,
        "charger": p.charger,
        "power": p.power,
        "chargerPower": p.charger_power,
        "image": p.image,
        "images": p.images,
        "exact": p.exact,
        "verified": p.verified,
        "sourceUrl": p.source_url,
        "officialProductPage": p.official_product_page,
    }
    for k, v in (p.extra or {}).items():
        d.setdefault(k, v)
    return d


def all_products_as_dicts():
    return [product_to_dict(p) for p in Product.objects.all()]
