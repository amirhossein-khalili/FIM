# Generated by Django 5.0.6 on 2025-04-16 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("E", "Email"),
                    ("S", "Sms"),
                    ("P", "Push"),
                    ("D", "Dev"),
                    ("T", "Telegram"),
                ],
                help_text="Type of notification",
                max_length=10,
            ),
        ),
    ]
