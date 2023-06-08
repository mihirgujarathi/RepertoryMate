from django.contrib import admin
from .models import Patient_Medical_History, Medical_Narcotics_Sports_History, Doctor_Profile, User_Feedback


admin.site.register(Patient_Medical_History)
admin.site.register(Medical_Narcotics_Sports_History)
admin.site.register(Doctor_Profile)
admin.site.register(User_Feedback)