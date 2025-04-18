# Generated by Django 5.1.4 on 2025-04-13 01:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_remove_profile_cards_profile_cards"),
        ("pokemon", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="cards",
        ),
        migrations.CreateModel(
            name="ProfileCards",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cards",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="pokemon.card"
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.profile",
                    ),
                ),
            ],
        ),
    ]
