# Generated by Django 2.0.4 on 2018-05-20 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_auto_20180518_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='BookNum',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='account',
            name='CommentNum',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='account',
            name='RecordNum',
            field=models.PositiveIntegerField(default=1),
        ),
    ]