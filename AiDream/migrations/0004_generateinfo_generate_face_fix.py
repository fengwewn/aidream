# Generated by Django 4.1.5 on 2023-01-20 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AiDream', '0003_remove_generateinfo_generate_tag_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='generateinfo',
            name='generate_face_fix',
            field=models.BooleanField(default=False, verbose_name='面部修复'),
        ),
    ]
