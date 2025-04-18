# Generated by Django 5.1.4 on 2025-04-12 05:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Pokemon",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("pokedexNumber", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Card",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("type", models.CharField(max_length=100)),
                ("hp", models.FloatField()),
                ("small_image", models.CharField(max_length=100)),
                ("large_image", models.CharField(max_length=100)),
                (
                    "pokemon_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pokemon.pokemon",
                    ),
                ),
            ],
        ),
    ]
