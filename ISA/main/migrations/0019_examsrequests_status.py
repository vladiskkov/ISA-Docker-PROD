# Generated by Django 4.1.7 on 2023-03-28 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_examsrequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='examsrequests',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
