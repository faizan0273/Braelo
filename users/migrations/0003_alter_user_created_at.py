# Generated by Django 4.2.15 on 2024-08-31 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_first_name_alter_user_last_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="created_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
