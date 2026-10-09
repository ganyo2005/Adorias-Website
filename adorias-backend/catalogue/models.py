from django.db import models


class Product(models.Model):
    # Position in the original catalogue.js array. A couple of the ported
    # Efia ranking functions break score ties by relying on stable-sort
    # array order rather than an explicit secondary key, so this has to be
    # preserved for the Python port to rank identically to the original JS.
    import_order = models.PositiveIntegerField(default=0, db_index=True)

    sku = models.CharField(max_length=16, primary_key=True)
    brand = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=128)
    category = models.CharField(max_length=64, db_index=True)
    original_category = models.CharField(max_length=64, blank=True)
    model = models.CharField(max_length=128, blank=True)

    specs = models.TextField(blank=True)
    key_specifications = models.TextField(blank=True)
    description = models.TextField(blank=True)
    compatibility = models.TextField(blank=True)
    use_cases = models.TextField(blank=True)

    battery = models.CharField(max_length=128, blank=True)
    charger = models.CharField(max_length=128, blank=True)
    power = models.CharField(max_length=128, blank=True)
    charger_power = models.CharField(max_length=128, blank=True)

    image = models.CharField(max_length=256, blank=True)
    images = models.JSONField(default=list, blank=True)

    exact = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    source_url = models.URLField(max_length=512, blank=True)
    official_product_page = models.URLField(max_length=512, blank=True)

    # Populated from the "Other Products Image Catalogue" research tool
    # (a manual image-sourcing checklist for the 377 non-camera/camcorder
    # products still missing local photos). Finer-grained than category,
    # and image_sourcing_status tracks how confidently that exact model can
    # be identified before a photo is sourced for it.
    subcategory = models.CharField(max_length=64, blank=True)
    image_slug = models.CharField(max_length=128, blank=True)
    image_sourcing_status = models.CharField(max_length=256, blank=True)

    # Free-form provenance/audit trail fields preserved verbatim from the
    # original catalogue.js export, kept as-is rather than modeled as
    # columns since they are internal QA notes, not customer/Efia-facing data.
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["import_order"]

    def __str__(self):
        return f"{self.sku} — {self.name}"
