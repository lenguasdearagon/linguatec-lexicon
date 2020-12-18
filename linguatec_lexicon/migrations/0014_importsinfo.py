# Generated by Django 2.2.13 on 2020-12-12 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linguatec_lexicon', '0013_auto_20201114_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('created', 'CREATED'), ('running', 'RUNNING'), ('failed', 'FAILED'), ('completed', 'COMPLETED'), ('completed with errors', 'COMPLETED WITH ERRORS')], max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('data', 'DATA'), ('variation', 'VARIATION'), ('gramcats', 'GRAMCATS')], max_length=25)),
                ('errors', models.TextField(blank=True)),
                ('num_rows', models.IntegerField(null=True)),
                ('input_file', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
