import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalogue.models import Product


class Command(BaseCommand):
    help = (
        "Import subcategory/slug/verification-status metadata from the "
        "'Other Products Image Catalogue' research tool (an HTML page whose "
        "embedded `const ITEMS=[...]` array lists the non-camera/camcorder "
        "products still missing local photos) into matching Product rows."
    )

    def add_arguments(self, parser):
        parser.add_argument("html_path", help="Path to the Adorias_Other_Products_*.html file")

    def handle(self, *args, **options):
        path = Path(options["html_path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")
        content = path.read_text(encoding="utf-8")

        marker = "const ITEMS="
        idx = content.find(marker)
        if idx == -1:
            raise CommandError("Could not find 'const ITEMS=' in the file.")
        items, _ = json.JSONDecoder().raw_decode(content, idx + len(marker))

        updated, missing = 0, []
        for it in items:
            n = Product.objects.filter(sku=it["sku"]).update(
                subcategory=it.get("subcategory") or "",
                image_slug=it.get("slug") or "",
                image_sourcing_status=it.get("verification") or "",
            )
            if n:
                updated += 1
            else:
                missing.append(it["sku"])

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated}/{len(items)} products with image-sourcing metadata."
        ))
        if missing:
            self.stdout.write(self.style.WARNING(
                f"{len(missing)} SKUs from the tool were not found in the catalogue: {missing[:20]}"
            ))
