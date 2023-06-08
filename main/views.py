from django.shortcuts import render, redirect, HttpResponse
from .models import *
from accounts.models import *
from django.contrib.auth.models import User
import json
import operator as op
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# getting the question data in variable "questionnaire_data"
with open("questions_data.json", "r") as f:
    questionnaire_data = json.load(f)


# getting the BCMR data in variable "bcmr_db"
with open("bcmr_db.json", "r") as f:
    bcmr_db = json.load(f)


def get_mappedcasesheets(request):
    mappedcasesheets = Patient_Case_Sheet.objects.filter(
        user=request.user, case_sheet_name=request.session.get("casesheetname")
    )
    return mappedcasesheets


def does_question_exist(question_number, mappedcasesheets):
    question_number_temp = int(question_number)
    question_name = "Q" + str(question_number_temp)

    while (
        question_number_temp < 36
        and questionnaire_data[question_name][mappedcasesheets[0].majorlocation][
            mappedcasesheets[0].minorlocation
        ][mappedcasesheets[0].problem]["question"]
        == ""
    ):
        question_number_temp += 1
        question_name = "Q" + str(question_number_temp)

    if int(question_number) == question_number_temp:
        return True, None
    else:
        return False, question_number_temp


def getFinalStringforMultipleCorrectQuestions(options_selected):
    finalString = options_selected[0]  # stores what to put in DB

    # putting all array values into one string
    for item in range(1, len(options_selected)):
        finalString += "$"
        finalString += options_selected[item]

    return finalString


def get_returndict(questiontype, question_number, mappedcasesheets, request):
    returndict = {}
    question_name = "Q" + str(question_number)

    if questiontype == "SingleCorrect":
        returndict = {
            "question": questionnaire_data[question_name][
                mappedcasesheets[0].majorlocation
            ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem][
                "question"
            ],
            "options": questionnaire_data[question_name][
                mappedcasesheets[0].majorlocation
            ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem][
                "options"
            ],
            "casesheetname": request.session.get("casesheetname"),
            "question_name": "question" + str(question_number),
        }

    else:
        optionheadings = []
        options = []

        # for filling option-headings
        for item in questionnaire_data[question_name][
            mappedcasesheets[0].majorlocation
        ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem]["options"]:
            optionheadings.append(item)

        # for the filling the options under each option heading
        for item in optionheadings:
            options.append(
                questionnaire_data[question_name][mappedcasesheets[0].majorlocation][
                    mappedcasesheets[0].minorlocation
                ][mappedcasesheets[0].problem]["options"][item]
            )

        returndict = {
            "question": questionnaire_data[question_name][
                mappedcasesheets[0].majorlocation
            ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem][
                "question"
            ],
            "headingsWithOptions": zip(optionheadings, options),
            "numberOfHeadings": len(options),
            "casesheetname": request.session.get("casesheetname"),
            "question_name": "question" + str(question_number),
        }

    return returndict


def get_returndict_singlecorrectsubrubrics(
    savedanswer, question_number, subrubrics_array, mappedcasesheets, request
):
    returndict = {}
    question_name = "Q" + str(question_number)

    returndict = {
        "question": questionnaire_data[question_name][
            mappedcasesheets[0].majorlocation
        ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem]["question"],
        "old_option": savedanswer,
        "options": subrubrics_array,
        "casesheetname": request.session.get("casesheetname"),
        "question_name": "question" + str(question_number),
    }

    return returndict


def get_returndict_multicorrectsubrubrics(question_number, mappedcasesheets, request):
    returndict = {}
    question_name = "Q" + str(question_number)

    returndict = {
        "question": questionnaire_data[question_name][
            mappedcasesheets[0].majorlocation
        ][mappedcasesheets[0].minorlocation][mappedcasesheets[0].problem]["question"],
        "casesheetname": request.session.get("casesheetname"),
        "question_name": "question" + str(question_number),
    }

    return returndict


# helper function for handling subrubrics
def get_subrubrics_singlecorrect(mappedcasesheets, stored_answer, question_name):
    # getting majorlocation
    majorlocation = mappedcasesheets[0].majorlocation

    # getting minorlocation
    minorlocation = mappedcasesheets[0].minorlocation

    # getting problem
    problem = mappedcasesheets[0].problem

    # this dict will store the dict of stored_answer
    dict_of_rubric = {}

    # this array will store the list of sub-rubrics
    subrubric_array = []

    # stored_answer contains the rubric/rubrics stored inside the casesheet database for the particular question

    # processing the question

    # check if that question exists, if it doesn't, no need to process it. Also if the options aren't rubrics then no need to process them
    if stored_answer is not None:
        is_rubric = questionnaire_data[question_name][majorlocation][minorlocation][
            problem
        ]["is_rubrics"]

        # if the options aren't rubrics then no need to process them, if they aren't rubrics, the function will return an empty array
        if is_rubric == "True" and "None of the above" not in stored_answer:
            where_are_rubrics = questionnaire_data[question_name][majorlocation][
                minorlocation
            ][problem]["where"]
            rubrics_array = where_are_rubrics.split("->")

            # reaching the dict_of_question in bcmr database using the "where" in the questionnaire_data
            dict_of_rubric = bcmr_db[majorlocation]
            # can't run the below loop from 0 as if we don't do "dict_of_rubric = bcmr_db[majorlocation]" then the dict_of_rubric is empty, so the line "dict_of_rubric = dict_of_rubric[rubrics_array[i]]" will give error
            for i in range(1, len(rubrics_array)):
                dict_of_rubric = dict_of_rubric[rubrics_array[i]]

            dict_of_rubric_uptill_where = dict_of_rubric

            # the following few lines of code splits the string by "->" as well as "~>", so first we split by "->" then by "~>" and then store the parts in optionparts_array
            splitparts_array = stored_answer.split("->")
            optionparts_array = []
            for item in splitparts_array:
                array = item.split("~>")
                for smallitem in array:
                    optionparts_array.append(smallitem)

            # adding the selected option to the dict_of_question to get the solution
            for option_part in optionparts_array:
                dict_of_rubric = dict_of_rubric[option_part]

        if dict_of_rubric != {}:
            for item in dict_of_rubric:
                if type(dict_of_rubric[item]) == dict:
                    subrubric_array.append(item)

        subrubric_array.append("None of the above")
    return subrubric_array


def get_subrubrics_multicorrect(mappedcasesheets, stored_answer, question_name):
    # getting majorlocation
    majorlocation = mappedcasesheets[0].majorlocation

    # getting minorlocation
    minorlocation = mappedcasesheets[0].minorlocation

    # getting problem
    problem = mappedcasesheets[0].problem

    # this array will store the final array that we need to return
    finalarray = None
    # stored_answer contains the rubric/rubrics stored inside the casesheet database for the particular question

    # processing the question

    # check if that question exists, if it doesn't, no need to process it. Also if the options aren't rubrics then no need to process them
    if stored_answer is not None:
        is_rubric = questionnaire_data[question_name][majorlocation][minorlocation][
            problem
        ]["is_rubrics"]

        # if the options aren't rubrics then no need to process them
        if is_rubric == "True":
            where_are_rubrics = questionnaire_data[question_name][majorlocation][
                minorlocation
            ][problem]["where"]
            rubrics_array = where_are_rubrics.split("->")

            # reaching the dict_of_question in bcmr database using the "where" in the questionnaire_data
            dict_of_rubric = bcmr_db[majorlocation]
            # can't run the below loop from 0 as if we don't do "dict_of_rubric = bcmr_db[majorlocation]" then the dict_of_rubric is empty, so the line "dict_of_rubric = dict_of_rubric[rubrics_array[i]]" will give error
            for i in range(1, len(rubrics_array)):
                dict_of_rubric = dict_of_rubric[rubrics_array[i]]

            dict_of_rubric_uptill_where = dict_of_rubric
            # checking if its a multiple correct question or single correct
            selected_options_array = stored_answer.split("$")
            selected_options_subrubrics_array = []
            for selected_option in selected_options_array:
                subrubricarray = []
                dict_of_rubric = dict_of_rubric_uptill_where
                # adding the selected option to the dict_of_question to get the solution

                splitparts_array = selected_option.split("->")
                optionparts_array = []
                for item in splitparts_array:
                    array = item.split("~>")
                    for smallitem in array:
                        optionparts_array.append(smallitem)

                if "None of the above" in optionparts_array:
                    subrubricarray.append("")
                    selected_options_subrubrics_array.append(subrubricarray)
                else:
                    for option_part in optionparts_array:
                        dict_of_rubric = dict_of_rubric[option_part]

                    # adding subrubrics
                    for drug in dict_of_rubric:
                        drug_name = str(drug)
                        # checks that we are dealing with a sub-rubric and not a drug
                        if type(dict_of_rubric[drug_name]) == dict:
                            subrubricarray.append(drug_name)

                    subrubricarray.append("None of the above")
                    selected_options_subrubrics_array.append(subrubricarray)

            # returning all the selected options with their subrubrics. In the form of a 3-d array whose structure is......array[0] is an array of previously selected options, a 1-d array, and array[1] is a 2-d array of all the subrubrics of those options

            # now we checking whether the data we will be sending now is useful or not, as in, if it only contains None of the above and empty options, then why bother processing it, right?

            all_none_of_the_above_or_useless_options = False

            countofitems = len(selected_options_array)

            countofNoneoftheaboves = 0
            countofuselessoptions = 0
            for item in selected_options_array:
                if "None of the above" in item:
                    countofNoneoftheaboves += 1

            for item in selected_options_subrubrics_array:
                if len(item) == 1 and ("None of the above" in item or "" in item):
                    countofuselessoptions += 1

            if (
                countofNoneoftheaboves == countofitems
                or countofuselessoptions == countofitems
            ):
                all_none_of_the_above_or_useless_options = True

            finalarray = zip(selected_options_array, selected_options_subrubrics_array)

            returned_list = [finalarray, all_none_of_the_above_or_useless_options]
            return returned_list

    returned_list = [finalarray, False]
    return returned_list


def sub_rubric_handler_singlecorrect(request, question_number):
    # question_field_name contains the name of the currect question field in consideration
    question_field_name = "q" + question_number

    # current_question_sub_rubric_handler stores the name of the function which called this function. This variable stores strings like "sub_rubric_handler_q4"
    current_question_sub_rubric_handler = "sub_rubric_handler_q" + question_number

    # question_field_name contains the name of the currect question field in consideration
    question_field_name = "q" + question_number

    # question_name contains the name of question as stored in the questionnaire
    question_name = "Q" + question_number

    # next_question_function stores the name of the view of the next question
    next_question_function = "question" + str(int(question_number) + 1)

    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)
        savedanswer = getattr(mappedcasesheets[0], question_field_name)

        subrubrics_array = get_subrubrics_singlecorrect(
            mappedcasesheets, savedanswer, question_name
        )
        # if the subrubrics array gives us only ["None of the above"] then go to next question, otherwise continue
        if len(subrubrics_array) == 1:
            return redirect(next_question_function)
        # now prepare a returndict for sending this data to a template, send the question, the option selected before, the list of subrubrics, request.session for casesheetname
        # question_name[1:] gives us the "question number"
        returndict = get_returndict_singlecorrectsubrubrics(
            savedanswer, question_name[1:], subrubrics_array, mappedcasesheets, request
        )

        data_dict = fillval(mappedcasesheets[0])

        return render(
            request,
            "question_type_singlecorrect_subrubric.html",
            {"returndict": returndict, "data_dict": data_dict},
        )

    else:
        # get the selected option
        # now we need to update the previous answer. get the previous answer and add a "->" to it and after that add the selected option.
        # call this function again, if the subrubrics array gives us only ["None of the above"] then move forward, otherwise repeat the whole thing

        optionselected = request.POST["selectedoption"]
        casesheetname = request.POST["currentscasesheetname"]
        currentuser = request.user
        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )

        savedanswer = getattr(mappedcasesheets[0], question_field_name)
        newanswer = savedanswer

        if savedanswer is not None and optionselected != "None of the above":
            newanswer += "->" + optionselected
        else:
            # if we got "None of the above" then no changes required so, just go to the next question. Also we can't rely on the "GET" part for this function to take us there because it would again give us the same rubrics and this will become an infinite loop.
            return redirect(next_question_function)

        # checks if we got multiple casesheets of same name
        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(**{question_field_name: newanswer})
        else:
            return HttpResponse("Something went wrong!!!")

        return redirect(current_question_sub_rubric_handler)


def sub_rubric_handler_multicorrect(request, question_number):
    # question_field_name contains the name of the currect question field in consideration
    question_field_name = "q" + question_number

    # current_question_sub_rubric_handler stores the name of the function which called this function. This variable stores strings like "sub_rubric_handler_q4"
    current_question_sub_rubric_handler = "sub_rubric_handler_q" + question_number

    # question_name contains the name of question as stored in the questionnaire
    question_name = "Q" + question_number

    # next_question_function stores the name of the view of the next question
    next_question_function = ""
    if question_number != "35":
        next_question_function = "question" + str(int(question_number) + 1)
    else:
        next_question_function = "casesheet_saved"

    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)
        savedanswer = getattr(mappedcasesheets[0], question_field_name)

        returned_list = get_subrubrics_multicorrect(
            mappedcasesheets, savedanswer, question_name
        )

        shouldcontinue = False
        if returned_list[0] is not None and returned_list[1] == False:
            shouldcontinue = True

        # if the all the subrubrics array give us only ["None of the above"] then go to next question, otherwise continue

        if shouldcontinue == False:
            if next_question_function == "casesheet_saved":
                casesheetname = getattr(mappedcasesheets[0], "case_sheet_name")
                get_all_medicine_scores(request.user, casesheetname)
            storedanswer = getattr(mappedcasesheets[0], question_field_name)
            newanswer = storedanswer.replace("->None of the above", "")
            mappedcasesheets.update(**{question_field_name: newanswer})
            return redirect(next_question_function)

        returndict = get_returndict_multicorrectsubrubrics(
            question_number, mappedcasesheets, request
        )

        if returned_list is not None:
            returndict["options"] = returned_list[0]

        data_dict = fillval(mappedcasesheets[0])

        return render(
            request,
            "question_type_multicorrect_subrubric.html",
            {"returndict": returndict, "data_dict": data_dict},
        )

    else:
        # get the selected option
        # now we need to update the previous answer. get the previous answer and add a "->" to it and after that add the selected option. in case of multiple correct options, we need to find the option whose subrubrics we are dealing with right now and then do the same "->" thing.
        # call this function again, if the subrubrics array gives us only ["None of the above"] then move forward, otherwise repeat the whole thing

        oldoptions = request.POST.getlist("old_option")
        casesheetname = request.POST["currentscasesheetname"]
        currentuser = request.user
        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )
        newanswer = ""
        savedanswer = getattr(mappedcasesheets[0], question_field_name)

        for oldoption in oldoptions:
            new_option = request.POST[str(oldoption)]
            if savedanswer is not None:
                if new_option != "":
                    newanswer += oldoption + "->" + new_option + "$"
                else:
                    newanswer += oldoption + "$"
                    if len(oldoptions) == 1:
                        # if we got "None of the above" in the only option which had subrubrics then no changes required so, just go to the next question(nothing more to select now). Also we can't rely on the "GET" part for this function to take us there because it would again give us the same rubrics and this will become an infinite loop.
                        return redirect(next_question_function)

        # removing the last "$", "$" is used to seperate choices in multicorrect questions
        newanswer = newanswer[:-1]

        # checks if we got multiple casesheets of same name
        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(**{question_field_name: newanswer})
        else:
            return HttpResponse("Something went wrong!!!")

        return redirect(current_question_sub_rubric_handler)


# For converting queryset dict to actual dict with filled values
def fillval(all_dict):
    returndict = {
        "ques1": all_dict.question1,
        "ans1": all_dict.majorlocation,
        "ques2": all_dict.question2,
        "ans2": all_dict.minorlocation,
        "ques3": all_dict.question3,
        "ans3": all_dict.problem,
        "ques4": all_dict.question4,
        "ans4": all_dict.q4,
        "ques5": all_dict.question5,
        "ans5": all_dict.q5,
        "ques6": all_dict.question6,
        "ans6": all_dict.q6,
        "ques7": all_dict.question7,
        "ans7": all_dict.q7,
        "ques8": all_dict.question8,
        "ans8": all_dict.q8,
        "ques9": all_dict.question9,
        "ans9": all_dict.q9,
        "ques10": all_dict.question10,
        "ans10": all_dict.q10,
        "ques11": all_dict.question11,
        "ans11": all_dict.q11,
        "ques12": all_dict.question12,
        "ans12": all_dict.q12,
        "ques13": all_dict.question13,
        "ans13": all_dict.q13,
        "ques14": all_dict.question14,
        "ans14": all_dict.q14,
        "ques15": all_dict.question15,
        "ans15": all_dict.q15,
        "ques16": all_dict.question16,
        "ans16": all_dict.q16,
        "ques17": all_dict.question17,
        "ans17": all_dict.q17,
        "ques18": all_dict.question18,
        "ans18": all_dict.q18,
        "ques19": all_dict.question19,
        "ans19": all_dict.q19,
        "ques20": all_dict.question20,
        "ans20": all_dict.q20,
        "ques21": all_dict.question21,
        "ans21": all_dict.q21,
        "ques22": all_dict.question22,
        "ans22": all_dict.q22,
        "ques23": all_dict.question23,
        "ans23": all_dict.q23,
        "ques24": all_dict.question24,
        "ans24": all_dict.q24,
        "ques25": all_dict.question25,
        "ans25": all_dict.q25,
        "ques26": all_dict.question26,
        "ans26": all_dict.q26,
        "ques27": all_dict.question27,
        "ans27": all_dict.q27,
        "ques28": all_dict.question28,
        "ans28": all_dict.q28,
        "ques29": all_dict.question29,
        "ans29": all_dict.q29,
        "ques30": all_dict.question30,
        "ans30": all_dict.q30,
        "ques31": all_dict.question31,
        "ans31": all_dict.q31,
        "ques32": all_dict.question32,
        "ans32": all_dict.q32,
        "ques33": all_dict.question33,
        "ans33": all_dict.q33,
        "ques34": all_dict.question34,
        "ans34": all_dict.q34,
        "ques35": all_dict.question35,
        "ans35": all_dict.q35,
    }
    return returndict


def question_helper_singlecorrect(request, question_number):
    # question_field_name contains the name of the currect question field in consideration
    question_field_name = "q" + question_number

    # subrubric_function_for_this_question stores the name of the view of the subrubric handler for this question
    subrubric_function_for_this_question = "sub_rubric_handler_q" + question_number

    # question_to_store_in_database contains the variable name in model to store questions
    question_to_store_in_database = "question" + question_number

    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)

        question_exists = does_question_exist(
            question_number=question_number, mappedcasesheets=mappedcasesheets
        )

        if not question_exists[0]:
            # next_question_function stores the function name we need to visit next
            next_question_function = "question" + str(question_exists[1])
            if question_exists[1] > 35:
                return redirect("casesheet_saved")
            else:
                return redirect(next_question_function)

        returndict = get_returndict(
            questiontype="SingleCorrect",
            question_number=question_number,
            mappedcasesheets=mappedcasesheets,
            request=request,
        )

        data_dict = fillval(mappedcasesheets[0])

        return render(
            request,
            "question_type_singlecorrect.html",
            {"returndict": returndict, "data_dict": data_dict},
        )
    else:
        current_question = request.POST["current_question"]
        optionselected = request.POST["selectedoption"]
        casesheetname = request.POST["currentscasesheetname"]
        currentuser = request.user
        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )

        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(
                **{question_field_name: optionselected},
                **{question_to_store_in_database: current_question},
            )
        else:
            return HttpResponse("Something went wrong!!!")

        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )

        majorlocation = mappedcasesheets[0].majorlocation

        minorlocation = mappedcasesheets[0].minorlocation

        problem = mappedcasesheets[0].problem

        question_name = question_field_name.upper()

        is_rubric = questionnaire_data[question_name][majorlocation][minorlocation][
            problem
        ]["is_rubrics"]
        if is_rubric:
            return redirect(subrubric_function_for_this_question)
        else:
            return redirect("question" + str(int(question_number) + 1))


def question_helper_multicorrect(request, question_number):
    # question_field_name contains the name of the currect question field in consideration
    question_field_name = "q" + question_number

    # subrubric_function_for_this_question stores the name of the view of the subrubric handler for this question
    subrubric_function_for_this_question = "sub_rubric_handler_q" + question_number

    # next_question_function stores the name of the view of the next question
    next_question_function = ""

    # question_to_store_in_database contains the variable name in model to store questions
    question_to_store_in_database = "question" + question_number

    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)

        question_exists = does_question_exist(question_number, mappedcasesheets)

        if not question_exists[0]:
            # next_question_function stores the function name we need to visit next
            if question_exists[1] is not None and question_exists[1] < 36:
                next_question_function = "question" + str(question_exists[1])
            else:
                casesheetname = getattr(mappedcasesheets[0], "case_sheet_name")
                get_all_medicine_scores(request.user, casesheetname)
                next_question_function = "casesheet_saved"
            return redirect(next_question_function)

        returndict = get_returndict(
            questiontype="MultiCorrect",
            question_number=question_number,
            mappedcasesheets=mappedcasesheets,
            request=request,
        )

        data_dict = fillval(mappedcasesheets[0])

        return render(
            request,
            "question_type_multicorrect.html",
            {"returndict": returndict, "data_dict": data_dict},
        )
    else:
        current_question = request.POST["current_question"]
        options_selected = request.POST.getlist("selectedoption")
        casesheetname = request.POST["currentscasesheetname"]
        currentuser = request.user
        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )

        finalString = getFinalStringforMultipleCorrectQuestions(
            options_selected=options_selected
        )

        # checks if we got multiple casesheets of same name
        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(
                **{question_field_name: finalString},
                **{question_to_store_in_database: current_question},
            )
        else:
            return HttpResponse("Something went wrong!!!")

        mappedcasesheets = Patient_Case_Sheet.objects.filter(
            user=currentuser, case_sheet_name=casesheetname
        )

        majorlocation = mappedcasesheets[0].majorlocation

        minorlocation = mappedcasesheets[0].minorlocation

        problem = mappedcasesheets[0].problem

        question_name = question_field_name.upper()

        is_rubric = questionnaire_data[question_name][majorlocation][minorlocation][
            problem
        ]["is_rubrics"]
        if is_rubric:
            return redirect(subrubric_function_for_this_question)
        else:
            return redirect("question" + str(int(question_number) + 1))


# helper function for getting medicine scores


def get_medicine_scores(
    currentuser, casesheetname, stored_answer, medicine_scores, question_name
):
    mappedcasesheets = Patient_Case_Sheet.objects.filter(
        user=currentuser, case_sheet_name=casesheetname
    )

    # getting majorlocation
    majorlocation = mappedcasesheets[0].majorlocation

    # getting minorlocation
    minorlocation = mappedcasesheets[0].minorlocation

    # getting problem
    problem = mappedcasesheets[0].problem

    # stored_answer contains the rubric/rubrics stored inside the casesheet database for the particular question

    # processing the question

    # check if that question exists, if it doesn't, no need to process it. Also if the options aren't rubrics then no need to process them
    if stored_answer != None and stored_answer != "":
        is_rubric = questionnaire_data[question_name][majorlocation][minorlocation][
            problem
        ]["is_rubrics"]

        # if the options aren't rubrics then no need to process them
        if is_rubric == "True" and "None of the above" not in stored_answer:
            where_are_rubrics = questionnaire_data[question_name][majorlocation][
                minorlocation
            ][problem]["where"]
            rubrics_array = where_are_rubrics.split("->")

            # reaching the dict_of_question in bcmr database using the "where" in the questionnaire_data
            dict_of_rubric = bcmr_db[majorlocation]
            # can't run the below loop from 0 as if we don't do "dict_of_rubric = bcmr_db[majorlocation]" then the dict_of_rubric is empty, so the line "dict_of_rubric = dict_of_rubric[rubrics_array[i]]" will give error
            for i in range(1, len(rubrics_array)):
                dict_of_rubric = dict_of_rubric[rubrics_array[i]]

            dict_of_rubric_uptill_where = dict_of_rubric
            # checking if its a multiple correct question or single correct
            if "$" not in stored_answer:
                # adding the selected option to the dict_of_question to get the solution
                splitparts_array = stored_answer.split("->")
                optionparts_array = []
                for item in splitparts_array:
                    array = item.split("~>")
                    for smallitem in array:
                        optionparts_array.append(smallitem)

                for option_part in optionparts_array:
                    dict_of_rubric = dict_of_rubric[option_part]

                num_of_medicines = 0

                for drug in dict_of_rubric:
                    drug_name = str(drug)
                    if type(dict_of_rubric[drug_name]) == int:
                        num_of_medicines += 1

                # we don't need to calculate medicine score for a rubric which has no medicines, so we keep on checking and removing rubrics, if their dict is empty. For eg: if we have "Pain~>shoulder->deltoid", deltoid has no medicines, so we remove it, now we have "Pain~>shoulder", say, we still have no medicines in that dict, so we will remove again and then just take pain, if it has medicines in its dict
                while num_of_medicines < 1:
                    index_of_last_optionpart = stored_answer.rfind("->")
                    stored_answer = stored_answer[0:index_of_last_optionpart]

                    splitparts_array = stored_answer.split("->")
                    optionparts_array = []
                    for item in splitparts_array:
                        array = item.split("~>")
                        for smallitem in array:
                            optionparts_array.append(smallitem)

                    dict_of_rubric = dict_of_rubric_uptill_where
                    for option_part in optionparts_array:
                        dict_of_rubric = dict_of_rubric[option_part]

                    for drug in dict_of_rubric:
                        drug_name = str(drug)
                        if type(dict_of_rubric[drug_name]) == int:
                            num_of_medicines += 1

                # adding medicine scores
                for drug in dict_of_rubric:
                    drug_name = str(drug)
                    if type(dict_of_rubric[drug_name]) == int:
                        # drug already exists
                        if drug_name in medicine_scores.keys():
                            medicine_scores[drug_name] += dict_of_rubric[drug_name]
                        # drug needs to be added to the medicine scores
                        else:
                            medicine_scores[drug] = dict_of_rubric[drug_name]
            else:
                selected_options_array = stored_answer.split("$")
                for selected_option in selected_options_array:
                    dict_of_rubric = dict_of_rubric_uptill_where
                    # adding the selected option to the dict_of_question to get the solution

                    splitparts_array = selected_option.split("->")
                    optionparts_array = []
                    for item in splitparts_array:
                        array = item.split("~>")
                        for smallitem in array:
                            optionparts_array.append(smallitem)

                    for option_part in optionparts_array:
                        dict_of_rubric = dict_of_rubric[option_part]

                    num_of_medicines = 0

                    for drug in dict_of_rubric:
                        drug_name = str(drug)
                        if type(dict_of_rubric[drug_name]) == int:
                            num_of_medicines += 1

                    # we don't need to calculate medicine score for a rubric which has no medicines, so we keep on checking and removing rubrics, if their dict is empty. For eg: if we have "Pain~>shoulder->deltoid", deltoid has no medicines, so we remove it, now we have "Pain~>shoulder", say, we still have no medicines in that dict, so we will remove again and then just take pain, if it has medicines in its dict
                    while num_of_medicines < 1:
                        index_of_last_optionpart = selected_option.rfind("->")
                        if index_of_last_optionpart == -1:
                            break
                        selected_option = selected_option[0:index_of_last_optionpart]

                        splitparts_array = selected_option.split("->")
                        optionparts_array = []
                        for item in splitparts_array:
                            array = item.split("~>")
                            for smallitem in array:
                                optionparts_array.append(smallitem)

                        dict_of_rubric = dict_of_rubric_uptill_where
                        for option_part in optionparts_array:
                            dict_of_rubric = dict_of_rubric[option_part]

                        for drug in dict_of_rubric:
                            drug_name = str(drug)
                            if type(dict_of_rubric[drug_name]) == int:
                                num_of_medicines += 1

                    # adding medicine scores
                    for drug in dict_of_rubric:
                        drug_name = str(drug)
                        # checks that we are dealing with a drug and not a sub-rubric
                        if type(dict_of_rubric[drug_name]) == int:
                            # drug already exists
                            if drug in medicine_scores.keys():
                                medicine_scores[drug] += dict_of_rubric[drug_name]
                            # drug needs to be added to the medicine scores
                            else:
                                medicine_scores[drug] = dict_of_rubric[drug_name]

    return medicine_scores


# creating and redo-ing already existing casesheet
def createcasesheet(request):
    if request.method == "POST":
        if "newCase" in request.POST:
            casesheetname = request.POST["casesheetname"]

            if Patient_Case_Sheet.objects.filter(
                user=request.user, case_sheet_name=casesheetname
            ).exists():
                return render(
                    request,
                    "newcasesheet.html",
                    {
                        "casesheetname": casesheetname,
                        "error_message": "Casesheet already exists! Would you like to redo this casesheet again?",
                    },
                )

            newcasesheet = Patient_Case_Sheet.objects.create(
                user=request.user, case_sheet_name=casesheetname
            )
            newcasesheet.save()
            request.session["casesheetname"] = casesheetname
            return redirect("question1")

        if "updateCase" in request.POST:
            request.session["casesheetname"] = request.POST["casesheetnameconfirm"]
            mappedcasesheets = get_mappedcasesheets(request)
            mappedcasesheets.delete()
            casesheetname = request.session["casesheetname"]
            newcasesheet = Patient_Case_Sheet.objects.create(
                user=request.user, case_sheet_name=casesheetname
            )
            newcasesheet.save()

            return redirect("question1")

    return render(request, "newcasesheet.html")


def casesheet_saved(request):
    mappedcasheets = get_mappedcasesheets(request)
    data_dict = fillval(mappedcasheets[0])
    data_dict["casesheetname"] = mappedcasheets[0].case_sheet_name
    return render(request, "casesheet_saved.html", {"data_dict": data_dict})


# for major-location


def question1(request):
    if request.method == "GET":
        returndict = {
            "question": "Q1. What is the location of your complaint?",
            "options": [
                "Head Internal",
                "Head External",
                "Upper Extremities",
                "Lower Extremities",
            ],
            "casesheetname": request.session.get("casesheetname"),
            "question_name": "question1",
        }
        return render(
            request, "question_type_singlecorrect.html", {"returndict": returndict}
        )

    else:
        current_question = "Q1. What is the location of your complaint?"
        optionselected = request.POST["selectedoption"]
        mappedcasesheets = get_mappedcasesheets(request)

        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(
                majorlocation=optionselected, question1=current_question
            )
        else:
            return HttpResponse("Something went wrong!!!")

        return redirect("question2")


# for minor-location
def question2(request):
    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)

        data_dict = fillval(mappedcasesheets[0])

        returndict = {
            "question": "Q2. What is the sub-location of your complaint?",
            "options": questionnaire_data["Q2"][mappedcasesheets[0].majorlocation],
            "casesheetname": request.session.get("casesheetname"),
            "question_name": "question2",
        }
        return render(
            request,
            "question_type_singlecorrect.html",
            {"returndict": returndict, "data_dict": data_dict},
        )

    else:
        current_question = "Q2. What is the sub-location of your complaint?"
        optionselected = request.POST["selectedoption"]
        mappedcasesheets = get_mappedcasesheets(request)

        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(
                minorlocation=optionselected, question2=current_question
            )
        else:
            return HttpResponse("Something went wrong!!!")

        return redirect("question3")


# for problem
def question3(request):
    if request.method == "GET":
        mappedcasesheets = get_mappedcasesheets(request)

        data_dict = fillval(mappedcasesheets[0])

        returndict = {
            "question": "Q3. What is your complaint?",
            "options": questionnaire_data["Q3"][mappedcasesheets[0].majorlocation][
                mappedcasesheets[0].minorlocation
            ],
            "casesheetname": request.session.get("casesheetname"),
            "question_name": "question3",
        }
        return render(
            request,
            "question_type_singlecorrect.html",
            {"returndict": returndict, "data_dict": data_dict},
        )

    else:
        current_question = "Q3. What is your complaint?"
        optionselected = request.POST["selectedoption"]
        mappedcasesheets = get_mappedcasesheets(request)

        if mappedcasesheets and len(mappedcasesheets) == 1:
            mappedcasesheets.update(problem=optionselected, question3=current_question)
        else:
            return HttpResponse("Something went wrong!!!")

        return redirect("question4")


def question4(request):
    return question_helper_singlecorrect(request, "4")


def sub_rubric_handler_q4(request):
    return sub_rubric_handler_singlecorrect(request, "4")


def question5(request):
    return question_helper_singlecorrect(request, "5")


def sub_rubric_handler_q5(request):
    return sub_rubric_handler_singlecorrect(request, "5")


def question6(request):
    return question_helper_singlecorrect(request, "6")


def sub_rubric_handler_q6(request):
    return sub_rubric_handler_singlecorrect(request, "6")


def question7(request):
    return question_helper_singlecorrect(request, "7")


def sub_rubric_handler_q7(request):
    return sub_rubric_handler_singlecorrect(request, "7")


def question8(request):
    return question_helper_singlecorrect(request, "8")


def sub_rubric_handler_q8(request):
    return sub_rubric_handler_singlecorrect(request, "8")


def question9(request):
    return question_helper_singlecorrect(request, "9")


def sub_rubric_handler_q9(request):
    return sub_rubric_handler_singlecorrect(request, "9")


def question10(request):
    return question_helper_singlecorrect(request, "10")


def sub_rubric_handler_q10(request):
    return sub_rubric_handler_singlecorrect(request, "10")


def question11(request):
    return question_helper_singlecorrect(request, "11")


def sub_rubric_handler_q11(request):
    return sub_rubric_handler_singlecorrect(request, "11")


def question12(request):
    return question_helper_singlecorrect(request, "12")


def sub_rubric_handler_q12(request):
    return sub_rubric_handler_singlecorrect(request, "12")


def question13(request):
    return question_helper_singlecorrect(request, "13")


def sub_rubric_handler_q13(request):
    return sub_rubric_handler_singlecorrect(request, "13")


def question14(request):
    return question_helper_singlecorrect(request, "14")


def sub_rubric_handler_q14(request):
    return sub_rubric_handler_singlecorrect(request, "14")


def question15(request):
    return question_helper_singlecorrect(request, "15")


def sub_rubric_handler_q15(request):
    return sub_rubric_handler_singlecorrect(request, "15")


def question16(request):
    return question_helper_singlecorrect(request, "16")


def sub_rubric_handler_q16(request):
    return sub_rubric_handler_singlecorrect(request, "16")


def question17(request):
    return question_helper_singlecorrect(request, "17")


def sub_rubric_handler_q17(request):
    return sub_rubric_handler_singlecorrect(request, "17")


def question18(request):
    return question_helper_singlecorrect(request, "18")


def sub_rubric_handler_q18(request):
    return sub_rubric_handler_singlecorrect(request, "18")


def question19(request):
    return question_helper_singlecorrect(request, "19")


def sub_rubric_handler_q19(request):
    return sub_rubric_handler_singlecorrect(request, "19")


def question20(request):
    return question_helper_singlecorrect(request, "20")


def sub_rubric_handler_q20(request):
    return sub_rubric_handler_singlecorrect(request, "20")


def question21(request):
    return question_helper_singlecorrect(request, "21")


def sub_rubric_handler_q21(request):
    return sub_rubric_handler_singlecorrect(request, "21")


def question22(request):
    return question_helper_singlecorrect(request, "22")


def sub_rubric_handler_q22(request):
    return sub_rubric_handler_singlecorrect(request, "22")


def question23(request):
    return question_helper_singlecorrect(request, "23")


def sub_rubric_handler_q23(request):
    return sub_rubric_handler_singlecorrect(request, "23")


def question24(request):
    return question_helper_singlecorrect(request, "24")


def sub_rubric_handler_q24(request):
    return sub_rubric_handler_singlecorrect(request, "24")


def question25(request):
    return question_helper_singlecorrect(request, "25")


def sub_rubric_handler_q25(request):
    return sub_rubric_handler_singlecorrect(request, "25")


def question26(request):
    return question_helper_multicorrect(request, "26")


def sub_rubric_handler_q26(request):
    return sub_rubric_handler_multicorrect(request, "26")


def question27(request):
    return question_helper_multicorrect(request, "27")


def sub_rubric_handler_q27(request):
    return sub_rubric_handler_multicorrect(request, "27")


def question28(request):
    return question_helper_multicorrect(request, "28")


def sub_rubric_handler_q28(request):
    return sub_rubric_handler_multicorrect(request, "28")


def question29(request):
    return question_helper_multicorrect(request, "29")


def sub_rubric_handler_q29(request):
    return sub_rubric_handler_multicorrect(request, "29")


def question30(request):
    return question_helper_multicorrect(request, "30")


def sub_rubric_handler_q30(request):
    return sub_rubric_handler_multicorrect(request, "30")


def question31(request):
    return question_helper_multicorrect(request, "31")


def sub_rubric_handler_q31(request):
    return sub_rubric_handler_multicorrect(request, "31")


def question32(request):
    return question_helper_multicorrect(request, "32")


def sub_rubric_handler_q32(request):
    return sub_rubric_handler_multicorrect(request, "32")


def question33(request):
    return question_helper_multicorrect(request, "33")


def sub_rubric_handler_q33(request):
    return sub_rubric_handler_multicorrect(request, "33")


def question34(request):
    return question_helper_multicorrect(request, "34")


def sub_rubric_handler_q34(request):
    return sub_rubric_handler_multicorrect(request, "34")


def question35(request):
    return question_helper_multicorrect(request, "35")


def sub_rubric_handler_q35(request):
    return sub_rubric_handler_multicorrect(request, "35")


def edit_casesheet(request, pk):
    if request.method == "GET":
        casesheet = Patient_Case_Sheet.objects.get(id=pk)
        user_name = casesheet.user
        casesheetname = casesheet.case_sheet_name
        datadict = fillval(casesheet)
        # print(datadict)
        return render(
            request,
            "editCaseDoctor.html",
            {
                "obj_id": pk,
                "casesheetname": casesheetname,
                "patient_user": user_name,
                "data_dict": datadict,
            },
        )
    else:
        mappedcasesheet = Patient_Case_Sheet.objects.filter(id=pk)

        new_majorlocation = ""
        new_minorlocation = ""
        new_problem = ""
        new_q4 = ""
        new_q5 = ""
        new_q6 = ""
        new_q7 = ""
        new_q8 = ""
        new_q9 = ""
        new_q10 = ""
        new_q11 = ""
        new_q12 = ""
        new_q13 = ""
        new_q14 = ""
        new_q15 = ""
        new_q16 = ""
        new_q17 = ""
        new_q18 = ""
        new_q19 = ""
        new_q20 = ""
        new_q21 = ""
        new_q22 = ""
        new_q23 = ""
        new_q24 = ""
        new_q25 = ""
        new_q26 = ""
        new_q27 = ""
        new_q28 = ""
        new_q29 = ""
        new_q30 = ""
        new_q31 = ""
        new_q32 = ""
        new_q33 = ""
        new_q34 = ""
        new_q35 = ""

        temp = request.POST.get("OPTIONS_Q1")
        if temp is not None:
            new_majorlocation = temp

        temp = request.POST.get("OPTIONS_Q2")
        if temp is not None:
            new_minorlocation = temp

        temp = request.POST.get("OPTIONS_Q3")
        if temp is not None:
            new_problem = temp

        temp = request.POST.get("OPTIONS_Q4")
        if temp is not None:
            new_q4 = temp

        temp = request.POST.get("OPTIONS_Q5")
        if temp is not None:
            new_q5 = temp

        temp = request.POST.get("OPTIONS_Q6")
        if temp is not None:
            new_q6 = temp

        temp = request.POST.get("OPTIONS_Q7")
        if temp is not None:
            new_q7 = temp

        temp = request.POST.get("OPTIONS_Q8")
        if temp is not None:
            new_q8 = temp

        temp = request.POST.get("OPTIONS_Q9")
        if temp is not None:
            new_q9 = temp

        temp = request.POST.get("OPTIONS_Q10")
        if temp is not None:
            new_q10 = temp

        temp = request.POST.get("OPTIONS_Q11")
        if temp is not None:
            new_q11 = temp

        temp = request.POST.get("OPTIONS_Q12")
        if temp is not None:
            new_q12 = temp

        temp = request.POST.get("OPTIONS_Q13")
        if temp is not None:
            new_q13 = temp

        temp = request.POST.get("OPTIONS_Q14")
        if temp is not None:
            new_q14 = temp

        temp = request.POST.get("OPTIONS_Q15")
        if temp is not None:
            new_q15 = temp

        temp = request.POST.get("OPTIONS_Q16")
        if temp is not None:
            new_q16 = temp

        temp = request.POST.get("OPTIONS_Q17")
        if temp is not None:
            new_q17 = temp

        temp = request.POST.get("OPTIONS_Q18")
        if temp is not None:
            new_q18 = temp

        temp = request.POST.get("OPTIONS_Q19")
        if temp is not None:
            new_q19 = temp

        temp = request.POST.get("OPTIONS_Q20")
        if temp is not None:
            new_q20 = temp

        temp = request.POST.get("OPTIONS_Q21")
        if temp is not None:
            new_q21 = temp

        temp = request.POST.get("OPTIONS_Q22")
        if temp is not None:
            new_q22 = temp

        temp = request.POST.get("OPTIONS_Q23")
        if temp is not None:
            new_q23 = temp

        temp = request.POST.get("OPTIONS_Q24")
        if temp is not None:
            new_q24 = temp

        temp = request.POST.get("OPTIONS_Q25")
        if temp is not None:
            new_q25 = temp

        temp = request.POST.get("OPTIONS_Q26")
        if temp is not None:
            new_q26 = temp

        temp = request.POST.get("OPTIONS_Q27")
        if temp is not None:
            new_q27 = temp

        temp = request.POST.get("OPTIONS_Q28")
        if temp is not None:
            new_q28 = temp

        temp = request.POST.get("OPTIONS_Q29")
        if temp is not None:
            new_q29 = temp

        temp = request.POST.get("OPTIONS_Q30")
        if temp is not None:
            new_q30 = temp

        temp = request.POST.get("OPTIONS_Q31")
        if temp is not None:
            new_q31 = temp

        temp = request.POST.get("OPTIONS_Q32")
        if temp is not None:
            new_q32 = temp

        temp = request.POST.get("OPTIONS_Q33")
        if temp is not None:
            new_q33 = temp

        temp = request.POST.get("OPTIONS_Q34")
        if temp is not None:
            new_q34 = temp

        temp = request.POST.get("OPTIONS_Q35")
        if temp is not None:
            new_q35 = temp

        mappedcasesheet.update(
            majorlocation=new_majorlocation,
            minorlocation=new_minorlocation,
            problem=new_problem,
            q4=new_q4,
            q5=new_q5,
            q6=new_q6,
            q7=new_q7,
            q8=new_q8,
            q9=new_q9,
            q10=new_q10,
            q11=new_q11,
            q12=new_q12,
            q13=new_q13,
            q14=new_q14,
            q15=new_q15,
            q16=new_q16,
            q17=new_q17,
            q18=new_q18,
            q19=new_q19,
            q20=new_q20,
            q21=new_q21,
            q22=new_q22,
            q23=new_q23,
            q24=new_q24,
            q25=new_q25,
            q26=new_q26,
            q27=new_q27,
            q28=new_q28,
            q29=new_q29,
            q30=new_q30,
            q31=new_q31,
            q32=new_q32,
            q33=new_q33,
            q34=new_q34,
            q35=new_q35,
        )

        casesheetname = mappedcasesheet[0].case_sheet_name
        patient_user = mappedcasesheet[0].user

        get_all_medicine_scores(patient_user, casesheetname)

        return redirect("display_casesheet")


def display_casesheet(request):
    # FOR DOCTOR
    if Doctor_Profile.objects.filter(user=request.user).exists():
        if request.method == "POST":
            casesheetid = request.POST.get("selected_casesheet")
            if casesheetid:
                all_dict = Patient_Case_Sheet.objects.filter(id=casesheetid)
                all_dict = all_dict[0]
                returndict = fillval(all_dict)
                casesheetname = Patient_Case_Sheet.objects.get(
                    id=casesheetid
                ).case_sheet_name
                medicine_scores = all_dict.all_medicine_scores
                obj_id = all_dict.id
                return render(
                    request,
                    "displayCasesheet.html",
                    {
                        "casesheetname": casesheetname,
                        "returndict": returndict,
                        "obj_id": obj_id,
                        "medicine_scores": medicine_scores,
                        "doctor": True,
                    },
                )

            dr_edit = request.POST.get("dr_edit")
            if dr_edit:
                return redirect(edit_casesheet, pk=dr_edit)
                # return render(request, "editCaseDoctor.html", {"obj_id": dr_edit})

            patient_username = request.POST["patient_username"]
            patient_casesheetname = request.POST["patient_casesheetname"]

            if not User.objects.filter(username=patient_username).exists():
                return render(
                    request,
                    "displayDoctorCasesheet.html",
                    {
                        "error_message": patient_username + " doesn't exist in database",
                        "doctor": True,
                    },
                )

            patient_user_id = User.objects.filter(username=patient_username)
            patient_user_id = patient_user_id[0]


            if Patient_Case_Sheet.objects.filter(user=patient_user_id).exists():
                # When doctor enters ONLY Patient name
                if not patient_casesheetname:
                    print("Only Patient Name")
                    patient_records = Patient_Case_Sheet.objects.filter(
                        user=patient_user_id
                    ).order_by("case_sheet_name")
                    return render(
                        request,
                        "displayDoctorCasesheet.html",
                        {"doctor": True, "patient_records": patient_records},
                    )

                # When doctor enters Patient name AND casesheet name
                else:
                    print("Both Fields")
                    if Patient_Case_Sheet.objects.filter(
                        user=patient_user_id, case_sheet_name=patient_casesheetname
                    ).exists():
                        patient_records = Patient_Case_Sheet.objects.filter(
                            user=patient_user_id, case_sheet_name=patient_casesheetname
                        )
                        patient_records = patient_records[0]
                        returndict = fillval(patient_records)
                        casesheetname = patient_records.case_sheet_name
                        medicine_scores = patient_records.all_medicine_scores
                        obj_id = patient_records.id
                        return render(
                            request,
                            "displayCasesheet.html",
                            {
                                "casesheetname": casesheetname,
                                "returndict": returndict,
                                "medicine_scores": medicine_scores,
                                "obj_id": obj_id,
                                "doctor": True,
                            },
                        )
                    else:
                        return render(
                            request,
                            "displayDoctorCasesheet.html",
                            {
                                "error_message": patient_username + " found but cannot find his casesheet named "
                                + patient_casesheetname,
                                "doctor": True,
                            },
                        )

            else:

                if Patient_Medical_History.objects.filter(user=patient_user_id).exists():
                    return render(
                        request,
                        "displayDoctorCasesheet.html",
                        {"error_message": patient_username + " does not have any casesheets", "doctor": True},
                    )
                else:
                    return render(
                        request,
                        "displayDoctorCasesheet.html",
                        {"error_message": patient_username + " is actually a doctor", "doctor": True},
                    )

        return render(request, "displayDoctorCasesheet.html", {"doctor": True})

    # FOR PATIENT
    if request.method == "POST":
        print("IN POST")
        deleteID = request.POST["delete_casesheet"]
        print("DELETE ID: ", deleteID)
        if deleteID:
            print()
            print("DELETE")
            print()
            delete_record = Patient_Case_Sheet.objects.get(pk=deleteID)
            delete_record.delete()
            return redirect(display_casesheet)

        casesheetid = request.POST["selected_casesheet"]
        if casesheetid:
            all_dict = Patient_Case_Sheet.objects.filter(id=casesheetid)
            all_dict = all_dict[0]
            returndict = fillval(all_dict)
            casesheetname = Patient_Case_Sheet.objects.get(
                id=casesheetid
            ).case_sheet_name

            return render(
                request,
                "displayCasesheet.html",
                {
                    "casesheetname": casesheetname,
                    "returndict": returndict,
                    "obj_id": all_dict.id,
                },
            )

        casesheetname = request.POST["casesheetname"]
        if Patient_Case_Sheet.objects.filter(
            user=request.user, case_sheet_name=casesheetname
        ).exists():
            all_dict = Patient_Case_Sheet.objects.filter(
                user=request.user, case_sheet_name=casesheetname
            )
            all_dict = all_dict[0]
            returndict = fillval(all_dict)
            return render(
                request,
                "displayCasesheet.html",
                {"casesheetname": casesheetname, "returndict": returndict},
            )
        else:
            return render(
                request,
                "displayCasesheet.html",
                {"error_message": "Casesheet not found"},
            )

    all_dict = Patient_Case_Sheet.objects.filter(user=request.user).order_by(
        "case_sheet_name"
    )

    return render(request, "displayCasesheet.html", {"all_dict": all_dict})


def pdf_view(request, id):
    req_casesheet = Patient_Case_Sheet.objects.get(pk=id)
    returndict = fillval(req_casesheet)
    casesheetname = req_casesheet.case_sheet_name

    template_path = "singleCaseSheet.html"
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'filename="{req_casesheet.user}_{casesheetname}.pdf"'
    template = get_template(template_path)
    html = template.render({"casesheetname": casesheetname, "returndict": returndict})

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Some pisa error")
    return response


def pdf_download(request, id):
    req_casesheet = Patient_Case_Sheet.objects.get(pk=id)
    returndict = fillval(req_casesheet)
    casesheetname = req_casesheet.case_sheet_name

    template_path = "singleCaseSheet.html"
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{req_casesheet.user}_{casesheetname}.pdf"'
    template = get_template(template_path)
    html = template.render({"casesheetname": casesheetname, "returndict": returndict})

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Some pisa error")
    return response


# for medicine suggestions


def get_all_medicine_scores(currentuser, casesheetname):
    # storing medicines names beforehand isn't working
    medicine_scores = {}
    
    #Question 1-3 are not included in scoring, they do not need to
    mappedcasesheets = Patient_Case_Sheet.objects.filter(
        user=currentuser, case_sheet_name=casesheetname
    )

    if len(mappedcasesheets) > 1:
        print("")
        print("")
        print("more than 1 casesheets of same name")
        print("")
        print("")

    majorlocation = mappedcasesheets[0].majorlocation

    # getting minorlocation
    minorlocation = mappedcasesheets[0].minorlocation
    # finding minorlocation in DB, dict_of_minorlocation contains the medicines mapped to the minorlocation in bcmr_db
    dict_of_minorlocation = bcmr_db[majorlocation]["Locations"][minorlocation]

    # for question 3

    # check if that question exists-this is problem question, so always exists

    problem = mappedcasesheets[0].problem

    # // FOR QUESTION 4 //
    question_number = 4
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q4

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 5 //
    question_number = 5
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q5

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 6 //
    question_number = 6
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q6

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 7 //
    question_number = 7
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q7

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 8 //
    question_number = 8
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q8

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 9 //
    question_number = 9
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q9

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 10 //
    question_number = 10
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q10

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 11 //
    question_number = 11
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q11

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 12 //
    question_number = 12
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q12

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 13 //
    question_number = 13
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q13

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 14 //
    question_number = 14
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q14

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 15 //
    question_number = 15
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q15

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 16 //
    question_number = 16
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q16

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 17 //
    question_number = 17
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q17

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 18 //
    question_number = 18
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q18

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 19 //
    question_number = 19
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q19

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 20 //
    question_number = 20
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q20

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 21 //
    question_number = 21
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q21

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 22 //
    question_number = 22
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q22

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 23 //
    question_number = 23
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q23

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 24 //
    question_number = 24
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q24

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 25 //
    question_number = 25
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q25

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 26 //
    question_number = 26
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q26

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 27 //
    question_number = 27
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q27

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 28 //
    question_number = 28
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q28

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 29 //
    question_number = 29
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q29

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 30 //
    question_number = 30
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q30

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 31 //
    question_number = 31
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q31

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 32 //
    question_number = 32
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q32

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 33 //
    question_number = 33
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q33

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 34 //
    question_number = 34
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q34

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    # // FOR QUESTION 35 //
    question_number = 35
    question_name = "Q" + str(question_number)
    stored_answer = mappedcasesheets[0].q35

    # updating the medicine_scores to include the scoring for current question
    medicine_scores = get_medicine_scores(
        currentuser, casesheetname, stored_answer, medicine_scores, question_name
    )

    sorted_dict = {}

    sorted_dict = dict(
        sorted(medicine_scores.items(), key=op.itemgetter(1), reverse=True)
    )
    top_five_drugs = {}
    count = 5
    for item in sorted_dict:
        top_five_drugs[item] = sorted_dict[item]
        count -= 1
        if count <= 0:
            break

    with open("DictFile.txt", "w") as file:
        file.write(json.dumps(sorted_dict))

    with open("DictFile.txt", "r") as file:
        file_content = file.read()

    mappedcasesheets.update(
        all_medicine_scores=sorted_dict, top_medicine_scores=top_five_drugs
    )

    return
