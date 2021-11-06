# Generated by Django 3.0.5 on 2020-05-20 14:48

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
        ('community', '0003_auto_20200520_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='posts',
            field=models.ManyToManyField(related_name='posts_com', to='post.Post'),
        ),
        migrations.AlterField(
            model_name='community',
            name='custom_url',
            field=models.CharField(default='', error_messages={'invalid': 'Invalid url', 'unique': 'A user with that username already exists.'}, help_text='Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=50, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()]),
        ),
    ]