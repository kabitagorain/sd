# Generated by Django 4.2 on 2024-10-16 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_remove_sitemeta_instagram_alter_sitemeta_facebook_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemeta',
            name='return_address',
            field=models.TextField(default='E.D. Systems Tech Center3798 Oleander Ave #2 Fort Pierce, Florida 34982United States.'),
        ),
    ]
