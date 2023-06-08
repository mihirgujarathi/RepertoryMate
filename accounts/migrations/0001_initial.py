# Generated by Django 3.2.7 on 2022-09-13 09:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient_Medical_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marital_status', models.BooleanField()),
                ('date_of_birth', models.DateField()),
                ('age', models.IntegerField()),
                ('sex', models.CharField(max_length=1)),
                ('occupation', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('contact_number', models.CharField(max_length=10)),
                ('height', models.CharField(max_length=5)),
                ('weight', models.CharField(max_length=3)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Medical_Narcotics_Sports_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_history_asthama', models.BooleanField(default=False)),
                ('medical_history_infection', models.BooleanField(default=False)),
                ('medical_history_tuberculosis', models.BooleanField(default=False)),
                ('medical_history_thyroid', models.BooleanField(default=False)),
                ('medical_history_hypertension', models.BooleanField(default=False)),
                ('medical_history_diabetes', models.BooleanField(default=False)),
                ('narcotics_history_smoking', models.BooleanField(default=False)),
                ('narcotics_history_drugs', models.BooleanField(default=False)),
                ('narcotics_history_alcohol', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]