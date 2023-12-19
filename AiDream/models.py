from django.db import models
from datetime import datetime
# Create your models here.

class embeddingInfo(models.Model):
    embedding_id = models.CharField(max_length=50, verbose_name='模型ID')
    embedding_name = models.CharField(max_length=50, verbose_name='模型名称')
    embedding_creator = models.CharField(max_length=50, verbose_name='创建者')
    embedding_status = models.BooleanField(default=False, verbose_name='完成状态')
    embedding_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    class Meta:
        verbose_name = 'Tag模型信息'
        verbose_name_plural = 'Tag模型信息管理'

class generateInfo(models.Model):
    generate_id = models.CharField(max_length=50, verbose_name='生图ID')
    generate_keyword = models.JSONField(verbose_name='提示词')
    generate_opposite_keyword = models.JSONField(verbose_name='反向提示词')
    generate_width = models.IntegerField(verbose_name='宽度')
    generate_height = models.IntegerField(verbose_name='高度')
    generate_round = models.IntegerField(verbose_name='生成批次')
    generate_num = models.IntegerField(verbose_name='生成数量')
    generate_art_width = models.IntegerField(verbose_name='美术风格权重%')
    generate_art_step = models.IntegerField(verbose_name='美术风格迭代步数')
    generate_face_fix = models.BooleanField(default=False, verbose_name='面部修复')
    generate_seed = models.IntegerField(verbose_name='种子')
    generate_creator = models.CharField(max_length=50, verbose_name='创建者')
    generate_status = models.BooleanField(default=False, verbose_name='完成状态')
    generate_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    class Meta:
        verbose_name = '生图信息'
        verbose_name_plural = '生图信息管理'