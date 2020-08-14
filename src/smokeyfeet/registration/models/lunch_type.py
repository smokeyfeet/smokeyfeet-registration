from django.db import models


class LunchType(models.Model):
    class Meta:
        ordering = ["sort_order"]

    name = models.CharField(max_length=64)
    sort_order = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return "{} - €{}".format(self.name, self.unit_price)
