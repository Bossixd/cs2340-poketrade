import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0007_alter_profile_user'),
        ('pokemon', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1),
                                                                  django.core.validators.MaxValueValidator(999999)])),
                ('listed_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemon.card')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings',
                                             to='accounts.profile')),
            ],
            options={
                'ordering': ['-listed_at'],
            },
        ),
        migrations.CreateModel(
            name='ElementType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DesiredCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pity_counter', models.IntegerField(default=0)),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           to='pokemon.card')),
                ('profile',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='desired_card', to='accounts.profile')),
            ],
        ),
    ]