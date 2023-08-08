# Generated by Django 4.1.7 on 2023-03-16 16:08

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_aditionaluserinfo_manager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='description',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='name',
        ),
        migrations.CreateModel(
            name='ExamTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Екзамен')),
                ('description', models.CharField(default='Опис', max_length=1000, verbose_name='Опис')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='main.exam')),
            ],
            options={
                'verbose_name': 'exam Translation',
                'db_table': 'main_exam_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases = (parler.models.TranslatableModel, models.Model)
        ),
    ]
