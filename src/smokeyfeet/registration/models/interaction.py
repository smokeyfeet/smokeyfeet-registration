from django.db import models


class Interaction(models.Model):
    registration = models.ForeignKey(
        "registration.Registration", on_delete=models.CASCADE
    )

    description = models.TextField(max_length=4096, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
