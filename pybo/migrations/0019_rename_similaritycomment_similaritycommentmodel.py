# Generated by Django 4.2.16 on 2024-10-09 05:35

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pybo', '0018_rename_detectioncomment_detectioncommentmodel_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SimilarityComment',
            new_name='SimilarityCommentModel',
        ),
    ]
