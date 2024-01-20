from django.db import models


class Contact(models.Model):
    email = models.CharField(max_length=150)
    full_names = models.CharField(max_length=150)
    subject = models.CharField(max_length=400)
    message = models.TextField()

    def __str__(self):
        return self.email

