# Generated by Django 2.0.4 on 2018-05-12 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_comments_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='pict',
            field=models.ImageField(default='img/index.jpg', upload_to='image/%Y/%m/%d/'),
        ),
    ]