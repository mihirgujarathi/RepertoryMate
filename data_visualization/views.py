from django.shortcuts import render, HttpResponse, redirect
from accounts.models import Patient_Medical_History, Doctor_Profile, Medical_Narcotics_Sports_History
from main.models import Patient_Case_Sheet
from .utils import get_chart

# Create your views here.


def get_correct_question_val(val):
    if val == 'q1':
        val = 'majorlocation'
    if val == 'q2':
        val = 'minorlocation'
    if val == 'q3':
        val = 'problem'


def dv_home(request):
    if request.method == 'POST':
        val = request.POST['question_number']
        chart_type = request.POST.get('chart_type')
        returndict = {}
        title=val

        if val == 'height_vs_weight':
            chart_type = 'plot'
            data_height = Patient_Medical_History.objects.values('height')
            data_weight = Patient_Medical_History.objects.values('weight')

            for h,w in zip(data_height, data_weight):
                height = h['height']
                weight = w['weight']
                # count = len(Patient_Medical_History.objects.filter(**{val: d}))
                # print()
                # print()
                # print(height, " ", weight)
                # print()
                # print()

                returndict[int(height)] = int(weight)
        elif val[0] != 'q':
            data = Patient_Medical_History.objects.values(val).distinct()
            for dataa in data:
                d = dataa[f'{val}']
                count = len(Patient_Medical_History.objects.filter(**{val: d}))
                returndict[f'{d}'] = count
        else:
            search = title.replace("q","question")
            myv = Patient_Case_Sheet.objects.values(search)
            for v in myv:
                if v[search] is not None:
                    title = v[search]
            if val == 'q1':
                val = 'majorlocation'
            if val == 'q2':
                val = 'minorlocation'
            if val == 'q3':
                val = 'problem'
            print("Value ", val)
            data = Patient_Case_Sheet.objects.values(val).distinct()
            for dataa in data:
                d = dataa[f'{val}']
                count = len(Patient_Case_Sheet.objects.filter(**{val: d}))
                returndict[f'{d}'] = count

        print()
        print()
        print(val)
        print()
        print()

        chart = get_chart(returndict, chart_type, title)
        # chart = None
        return render(request, 'dv_home.html', {'chart': chart, 'current_question':val})
    return render(request, 'dv_home.html')
