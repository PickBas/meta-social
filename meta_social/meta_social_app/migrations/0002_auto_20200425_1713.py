# Generated by Django 3.0.5 on 2020-04-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta_social_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postimages',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='post/images/'),
        ),
    ]
