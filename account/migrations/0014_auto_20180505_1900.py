# Generated by Django 2.0.4 on 2018-05-05 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20180503_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comattitude',
            name='attitude',
            field=models.IntegerField(default=0),
        ),
    ]
