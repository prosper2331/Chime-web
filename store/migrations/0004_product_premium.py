# Generated by Django 4.2 on 2023-04-24 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_category_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='premium',
            field=models.BooleanField(default=False),
        ),
    ]
