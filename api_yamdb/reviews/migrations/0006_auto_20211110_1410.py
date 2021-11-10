# Generated by Django 2.2.16 on 2021-11-10 14:10

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20211110_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(blank=True, default=0, validators=[reviews.validators.score_validation], verbose_name='Оценка'),
        ),
    ]
