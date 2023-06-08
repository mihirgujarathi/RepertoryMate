from unittest.util import _MAX_LENGTH
from django.db.models.deletion import CASCADE
from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
import jsonfield

# MODELS

class Patient_Case_Sheet(models.Model):
    
    user = models.ForeignKey(User, on_delete=CASCADE)
    case_sheet_name = models.CharField(default="MyCaseSheet", max_length=50)

    question1 = models.CharField(null=True,max_length=1000)
    majorlocation = models.CharField(null=True, max_length=20)

    question2 = models.CharField(null=True,max_length=1000)
    minorlocation = models.CharField(null=True, max_length=50)

    question3 = models.CharField(null=True,max_length=1000)
    problem = models.CharField(null=True, max_length=30)

    question4 = models.CharField(null=True,max_length=1000)
    q4 = models.CharField(null=True, max_length=1000)

    question5 = models.CharField(null=True,max_length=1000)
    q5 = models.CharField(null=True, max_length=1000)

    question6 = models.CharField(null=True,max_length=1000)
    q6 = models.CharField(null=True, max_length=1000)

    question7 = models.CharField(null=True,max_length=1000)
    q7 = models.CharField(null=True, max_length=1000)

    question8 = models.CharField(null=True,max_length=1000)
    q8 = models.CharField(null=True, max_length=1000)

    question9 = models.CharField(null=True,max_length=1000)
    q9 = models.CharField(null=True, max_length=1000)

    question10 = models.CharField(null=True,max_length=1000)
    q10 = models.CharField(null=True, max_length=1000)

    question11 = models.CharField(null=True,max_length=1000)
    q11 = models.CharField(null=True, max_length=1000)

    question12 = models.CharField(null=True,max_length=1000)
    q12 = models.CharField(null=True, max_length=1000)

    question13 = models.CharField(null=True,max_length=1000)
    q13 = models.CharField(null=True, max_length=1000)

    question14 = models.CharField(null=True,max_length=1000)
    q14 = models.CharField(null=True, max_length=1000)

    question15 = models.CharField(null=True,max_length=1000)
    q15 = models.CharField(null=True, max_length=1000)

    question16 = models.CharField(null=True,max_length=1000)
    q16 = models.CharField(null=True, max_length=1000)

    question17 = models.CharField(null=True,max_length=1000)
    q17 = models.CharField(null=True, max_length=1000)
    
    question18 = models.CharField(null=True,max_length=1000)
    q18 = models.CharField(null=True, max_length=1000)

    question19 = models.CharField(null=True,max_length=1000)
    q19 = models.CharField(null=True, max_length=1000)

    question20 = models.CharField(null=True,max_length=1000)
    q20 = models.CharField(null=True, max_length=1000)

    question21 = models.CharField(null=True,max_length=1000)
    q21 = models.CharField(null=True, max_length=1000)

    question22 = models.CharField(null=True,max_length=1000)
    q22 = models.CharField(null=True, max_length=1000)

    question23 = models.CharField(null=True,max_length=1000)
    q23 = models.CharField(null=True, max_length=1000)

    question24 = models.CharField(null=True,max_length=1000)
    q24 = models.CharField(null=True, max_length=1000)

    question25 = models.CharField(null=True,max_length=1000)
    q25 = models.CharField(null=True, max_length=1000)

    question26 = models.CharField(null=True,max_length=1000)
    q26 = models.CharField(null=True, max_length=5000)

    question27 = models.CharField(null=True,max_length=1000)
    q27 = models.CharField(null=True, max_length=5000)

    question28 = models.CharField(null=True,max_length=1000)
    q28 = models.CharField(null=True, max_length=5000)

    question29 = models.CharField(null=True,max_length=1000)
    q29 = models.CharField(null=True, max_length=5000)

    question30 = models.CharField(null=True,max_length=1000)
    q30 = models.CharField(null=True, max_length=5000)

    question31 = models.CharField(null=True,max_length=1000)
    q31 = models.CharField(null=True, max_length=5000)

    question32 = models.CharField(null=True,max_length=1000)
    q32 = models.CharField(null=True, max_length=5000)

    question33 = models.CharField(null=True,max_length=1000)
    q33 = models.CharField(null=True, max_length=5000)

    question34 = models.CharField(null=True,max_length=1000)
    q34 = models.CharField(null=True, max_length=5000)

    question35 = models.CharField(null=True,max_length=1000)
    q35 = models.CharField(null=True, max_length=5000)

    all_medicine_scores = JSONField()
    top_medicine_scores = JSONField()

    def __str__(self):
        return str(str(self.user) + " -> " + self.case_sheet_name)
