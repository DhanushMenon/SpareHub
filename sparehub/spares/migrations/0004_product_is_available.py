# Generated by Django 5.0.7 on 2024-09-06 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spares', '0003_company_company_address_company_registration_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
