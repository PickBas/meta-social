# Generated by Django 3.0 on 2020-05-15 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_remove_music_user'),
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(blank=True, null=True)),
                ('plist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.Profile')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='music.Music')),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='playlist',
            field=models.ManyToManyField(related_name='playlist', through='user_profile.PlayPosition', to='music.Music'),
        ),
    ]
