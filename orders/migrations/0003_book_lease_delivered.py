# Generated by Django 5.0.3 on 2024-03-24 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_book_lease_leaseditem'),
    ]

    operations = [
        migrations.AddField(
            model_name='book_lease',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
    ]
