import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from catalogue.models import Product

PROMOTED_KEYS = {
    "sku", "brand", "name", "category", "originalCategory", "model",
    "specs", "keySpecifications", "description", "compatibility", "useCases",
    "battery", "charger", "power", "chargerPower",
    "image", "images", "exact", "verified", "sourceUrl", "officialProductPage",
}


class Command(BaseCommand):
    help = "Import the original catalogue.js product data (exported as catalogue_raw.json) into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(Path(settings.BASE_DIR) / "catalogue_raw.json"),
            help="Path to the raw catalogue JSON export.",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        data = json.loads(path.read_text())

        created, updated = 0, 0
        for index, raw in enumerate(data):
            extra = {k: v for k, v in raw.items() if k not in PROMOTED_KEYS}
            defaults = dict(
                import_order=index,
                brand=raw.get("brand") or "",
                name=raw.get("name") or "",
                category=raw.get("category") or "",
                original_category=raw.get("originalCategory") or "",
                model=raw.get("model") or "",
                specs=raw.get("specs") or "",
                key_specifications=raw.get("keySpecifications") or "",
                description=raw.get("description") or "",
                compatibility=raw.get("compatibility") or "",
                use_cases=raw.get("useCases") or "",
                battery=raw.get("battery") or "",
                charger=raw.get("charger") or "",
                power=raw.get("power") or "",
                charger_power=raw.get("chargerPower") or "",
                image=raw.get("image") or "",
                images=raw.get("images") or [],
                exact=bool(raw.get("exact")),
                verified=bool(raw.get("verified")),
                source_url=raw.get("sourceUrl") or "",
                official_product_page=raw.get("officialProductPage") or "",
                extra=extra,
            )
            _, was_created = Product.objects.update_or_create(sku=raw["sku"], defaults=defaults)
            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(data)} products ({created} created, {updated} updated)."
        ))
