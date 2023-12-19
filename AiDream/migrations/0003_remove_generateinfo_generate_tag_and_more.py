# Generated by Django 4.1.5 on 2023-01-19 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AiDream', '0002_generateinfo_alter_embeddinginfo_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generateinfo',
            name='generate_Tag',
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_art_step',
            field=models.IntegerField(default=1, verbose_name='美术风格迭代步数'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_art_width',
            field=models.IntegerField(default=1, verbose_name='美术风格权重%'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_height',
            field=models.IntegerField(default=1, verbose_name='高度'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_keyword',
            field=models.JSONField(default=1, verbose_name='提示词'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_num',
            field=models.IntegerField(default=1, verbose_name='生成数量'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_opposite_keyword',
            field=models.JSONField(default=1, verbose_name='反向提示词'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_round',
            field=models.IntegerField(default=1, verbose_name='生成批次'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_seed',
            field=models.IntegerField(default=1, verbose_name='种子'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='generateinfo',
            name='generate_width',
            field=models.IntegerField(default=1, verbose_name='宽度'),
            preserve_default=False,
        ),
    ]
