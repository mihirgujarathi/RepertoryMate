from unittest.util import _MAX_LENGTH
from django.db.models.deletion import CASCADE
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
import jsonfield


class User_Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    topic = models.CharField(max_length=30)
    feedback = models.CharField(max_length=1000)

    def __str__(self):
        return str(str(self.user) + " -> " + self.topic)

class Patient_Medical_History(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    marital_status = models.BooleanField()
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=6)
    occupation = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=10)
    height = models.CharField(max_length=5)
    weight = models.CharField(max_length=3)

    def __str__(self):
        return str(self.user)


class Medical_Narcotics_Sports_History(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    medical_history_asthma = models.BooleanField(default=False)
    medical_history_infection = models.BooleanField(default=False)
    medical_history_tuberculosis = models.BooleanField(default=False)
    medical_history_thyroid = models.BooleanField(default=False)
    medical_history_hypertension = models.BooleanField(default=False)
    medical_history_diabetes = models.BooleanField(default=False)
    narcotics_history_smoking = models.BooleanField(default=False)
    narcotics_history_drugs = models.BooleanField(default=False)
    narcotics_history_alcohol = models.BooleanField(default=False)
    sports_bool = models.BooleanField(default=False)
    sports_name = models.CharField(max_length=40, default="None")

    def __str__(self):
        return str(self.user)


class Doctor_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE, primary_key=True)
    specialization = models.CharField(default="None", max_length=20)
    Qualification = models.CharField(default="BHMRC", max_length=20)
    hospitalname = models.CharField(
        default="Bharati Vidyapeeth Homeopathy Hospital", max_length=100)

    def __str__(self):
        return str(self.user)
