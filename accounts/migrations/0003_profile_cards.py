# Generated by Django 5.1.4 on 2025-04-13 01:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_profile_currency"),
        ("pokemon", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="cards",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="pokemon.card",
            ),
        ),
    ]
