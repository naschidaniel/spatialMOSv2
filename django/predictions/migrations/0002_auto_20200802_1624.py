# Generated by Django 3.0.8 on 2020-08-02 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('predictions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialmosstep',
            name='spatialmos_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spatialmos_run', to='predictions.SpatialMosRun'),
        ),
        migrations.CreateModel(
            name='SpatialMosPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=14, default=None, max_digits=16)),
                ('lon', models.DecimalField(decimal_places=14, default=None, max_digits=16)),
                ('samos_mean', models.DecimalField(decimal_places=2, default=None, max_digits=6)),
                ('samos_spread', models.DecimalField(decimal_places=2, default=None, max_digits=6)),
                ('spatialmos_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spatialmos_step', to='predictions.SpatialMosStep')),
            ],
            options={
                'ordering': ('spatialmos_step', '-lat', 'lon'),
            },
        ),
        migrations.AddIndex(
            model_name='spatialmospoint',
            index=models.Index(fields=['spatialmos_step', 'lat', 'lon'], name='predictions_spatial_1c70af_idx'),
        ),
    ]