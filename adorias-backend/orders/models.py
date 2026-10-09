from django.db import models

WHATSAPP_NUMBER = "233249220653"


class SpecialOrder(models.Model):
    """A request submitted through the 'Special order' dialog.

    The original site's #specialForm collected these five fields but had no
    submit handler at all — clicking the button did nothing with them, and
    the only wired control sent a fixed generic WhatsApp message instead of
    the form's contents. This model/endpoint actually consumes the fields.
    """
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    brand_model = models.CharField(max_length=128)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.brand_model} x{self.quantity}"

    def whatsapp_message(self):
        lines = [
            f"Special order request from {self.name} ({self.phone}):",
            f"{self.quantity}x {self.brand_model}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)


class ProductEnquiry(models.Model):
    """A 'WhatsApp about this product' click from a product detail panel."""
    product_sku = models.CharField(max_length=16)
    product_name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Product enquiries"

    def __str__(self):
        return f"Enquiry: {self.product_name}"

    def whatsapp_message(self):
        return f"Hi Adorias, I'm interested in {self.product_name}"
