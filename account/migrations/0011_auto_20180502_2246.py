# Generated by Django 2.0.4 on 2018-05-02 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20180502_2213'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='content',
            field=models.TextField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='books',
            name='description',
            field=models.TextField(blank=True, default='', max_length=300),
        ),
    ]