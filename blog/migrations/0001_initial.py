# Generated by Django 5.1.4 on 2024-12-27 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('genre', models.CharField(max_length=100)),
                ('pages', models.CharField(max_length=50)),
                ('rating', models.CharField(max_length=10)),
                ('votes', models.CharField(max_length=50)),
                ('image', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('year', models.CharField(max_length=4)),
                ('genre', models.CharField(max_length=100)),
                ('duration', models.CharField(max_length=50)),
                ('rating', models.CharField(max_length=10)),
                ('image', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('year', models.CharField(max_length=4)),
                ('genre', models.CharField(max_length=100)),
                ('seasons', models.CharField(max_length=50)),
                ('rating', models.CharField(max_length=10)),
                ('image', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
