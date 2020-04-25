# Generated by Django 3.0.5 on 2020-04-25 18:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='first_part', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('info', models.CharField(max_length=1000, null=True)),
                ('base_image', models.ImageField(default='avatars/users/0.png', upload_to='avatars/communities')),
                ('image', models.ImageField(default='avatars/users/0.png', upload_to='avatars/communities')),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(related_name='users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Дата создания')),
                ('community', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='meta_social_app.Community')),
                ('likes', models.ManyToManyField(blank=True, related_name='likes', to='meta_social_app.Like')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Посты',
                'verbose_name_plural': 'Посты',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_image', models.ImageField(default='avatars/users/0.png', upload_to='avatars/users')),
                ('image', models.ImageField(default='avatars/users/0.png', upload_to='avatars/users')),
                ('job', models.CharField(max_length=100, null=True)),
                ('study', models.CharField(max_length=100, null=True)),
                ('biography', models.CharField(max_length=500, null=True)),
                ('gender', models.CharField(choices=[('M', 'Мужчина'), ('F', 'Женщина'), (None, 'Не указано')], max_length=1, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('birth', models.DateField(null=True)),
                ('show_email', models.BooleanField(default=False)),
                ('last_logout', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_act', models.DateTimeField(default=django.utils.timezone.now)),
                ('blacklist', models.ManyToManyField(related_name='blacklist', to=settings.AUTH_USER_MODEL)),
                ('chats', models.ManyToManyField(to='meta_social_app.Chat')),
                ('communities', models.ManyToManyField(to='meta_social_app.Community')),
                ('friends', models.ManyToManyField(related_name='friendlist', to=settings.AUTH_USER_MODEL)),
                ('liked_posts', models.ManyToManyField(related_name='liked_posts', to='meta_social_app.Post')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='post/images/')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta_social_app.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_file', models.FileField(upload_to='music')),
                ('artist', models.CharField(default='Автор', max_length=100, verbose_name='Автор')),
                ('title', models.CharField(default='Название', max_length=100, verbose_name='Название')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Музыка',
                'verbose_name_plural': 'Музыка',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='3+', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='4+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Дата')),
                ('text', models.CharField(max_length=500, verbose_name='Текст')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meta_social_app.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарий',
            },
        ),
        migrations.AddField(
            model_name='chat',
            name='messages',
            field=models.ManyToManyField(blank=True, to='meta_social_app.Message'),
        ),
        migrations.AddField(
            model_name='chat',
            name='second_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='second_part', to=settings.AUTH_USER_MODEL),
        ),
    ]
