# Generated by Django 5.0.7 on 2024-10-26 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spares', '0006_alter_company_user_alter_orderitem_quantity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('delivered', 'Delivered'), ('to_be_delivered', 'To be delivered')], default='to_be_delivered', max_length=20),
        ),
    ]