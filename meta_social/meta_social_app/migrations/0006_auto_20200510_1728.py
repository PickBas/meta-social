# Generated by Django 3.0.5 on 2020-05-10 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta_social_app', '0005_auto_20200503_0752'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='messages/images')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='images',
            field=models.ManyToManyField(to='meta_social_app.MessageImages'),
        ),
    ]
