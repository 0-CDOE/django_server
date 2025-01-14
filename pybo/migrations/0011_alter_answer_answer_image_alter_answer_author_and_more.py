# Generated by Django 4.2.16 on 2024-10-03 01:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pybo', '0010_alter_answer_id_alter_question_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer_image',
            field=models.ImageField(blank=True, null=True, upload_to='pybo/a_image', verbose_name='a_image'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='answer',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='pybo.question'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='voter',
            field=models.ManyToManyField(related_name='voter_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to='pybo/q_image1/', verbose_name='q_image1'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='pybo/q_image2/', verbose_name='q_image1'),
        ),
        migrations.AlterField(
            model_name='question',
            name='voter',
            field=models.ManyToManyField(related_name='voter_%(class)s', to=settings.AUTH_USER_MODEL),
        ),
    ]
