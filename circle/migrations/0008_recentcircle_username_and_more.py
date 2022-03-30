# Generated by Django 4.0.2 on 2022-03-28 21:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("login", "0004_userdata_password"),
        ("circle", "0007_recentcircle"),
    ]

    operations = [
        migrations.AddField(
            model_name="recentcircle",
            name="username",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="login.userdata",
            ),
        ),
        migrations.AlterField(
            model_name="recentcircle",
            name="recent_circle",
            field=models.TextField(default="[]", null=True),
        ),
    ]