# Generated by Django 2.1.5 on 2019-02-04 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linguatec_lexicon', '0005_auto_gramcat_abbr_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerbalConjugation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw', models.TextField(verbose_name='Raw imported content.')),
                ('entry', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='conjugation', to='linguatec_lexicon.Entry')),
            ],
        ),
    ]