# Generated by Django 2.1.1 on 2020-04-26 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salary', '0005_auto_20200303_2035'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticinformation',
            name='remark',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='备注'),
        ),
    ]
