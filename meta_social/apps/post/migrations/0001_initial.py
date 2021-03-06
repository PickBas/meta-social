# Generated by Django 3.0.5 on 2020-05-14 22:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('community',
                 models.ForeignKey(null=True,
                                   on_delete=django.db.models.deletion.CASCADE, to='community.Community')),
                ('likes', models.ManyToManyField(blank=True, related_name='likes', to='post.Like')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Посты',
                'verbose_name_plural': 'Посты',
            },
        ),
        migrations.CreateModel(
            name='PostImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='post/images/')),
                ('order', models.IntegerField(default=0)),
                ('from_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                                to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to='post.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Дата')),
                ('text', models.CharField(max_length=500, verbose_name='Текст')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to='post.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарий',
            },
        ),
    ]
