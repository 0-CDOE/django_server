# Generated by Django 4.2.16 on 2024-09-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0009_auto_20240923_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='question',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]