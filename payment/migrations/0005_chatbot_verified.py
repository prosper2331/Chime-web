# Generated by Django 4.2 on 2024-04-30 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbot',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
