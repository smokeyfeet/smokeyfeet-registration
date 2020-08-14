from django.db import models


class PassType(models.Model):
    class Meta:
        ordering = ["sort_order"]

    PASS_PARTY = "party"
    PASS_FULL = "full"
    PASS_TYPES = [(PASS_PARTY, "Party Pass"), (PASS_FULL, "Full Pass")]

    type = models.CharField(max_length=32, choices=PASS_TYPES)
    name = models.CharField(max_length=64)
    active = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField()
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    data = models.JSONField(blank=True)

    def __str__(self):
        s = "{} - €{}".format(self.name, self.unit_price)
        if self.video_audition_required:
            s += " - video audition"
        return s

    @property
    def video_audition_required(self):
        return self.data.get("video_audition_required", False)
