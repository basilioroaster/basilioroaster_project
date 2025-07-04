# Generated by Django 5.2.3 on 2025-06-20 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssociatedImages",
            fields=[
                ("image_id", models.AutoField(primary_key=True, serialize=False)),
                ("image_url", models.TextField()),
                ("description", models.TextField(blank=True, null=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Associated Images",
            },
        ),
    ]
