# Generated by Django 3.0.9 on 2020-08-06 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0006_auto_20200806_1228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spatialmosrun',
            name='timestamp',
        ),
        migrations.AlterField(
            model_name='spatialmosstep',
            name='spatialmos_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='predictions.SpatialMosRun'),
        ),
    ]