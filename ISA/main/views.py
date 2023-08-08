import json
from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, resolve_url
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import HttpResponse, HttpResponsePermanentRedirect
from wsgiref.util import FileWrapper
from os import path
from django.conf import settings
from django.utils import translation
from django.http import Http404, JsonResponse
from functools import wraps
from pathlib import Path
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime, timedelta
from urllib.parse import urlencode
from django.contrib import messages
from django.urls import reverse
from os import environ


def set_language_from_url(request, user_language):
    translation.activate(user_language)
    user_language = lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    redirect_to = request.META.get('HTTP_REFERER', reverse('exams'))
    return HttpResponseRedirect(redirect_to)

@login_required
def index(request):
    try:
        user = request.user
        credential = ClientSecretCredential(tenant_id=tenant_id, client_secret=client_secret, client_id=client_id)
        client = GraphClient(credential=credential)
        # result = client.get('/users/' + str(user), params={'$select': 'department, jobTitle, onPremisesDistinguishedName'})
        result = client.get('/users/' + str(user), params={'$select': 'department, jobTitle, companyName, manager'})
        result = result.json()
        job_title = result['jobTitle']
        department = result['department']
        company = result['companyName']
        AditionalUserInfo.objects.filter(username=user).update(job_title=job_title, department=department, company=company)
    except:
        pass
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    context = {
        'unread_notifications': unread_notifications
    }
    return render(request, 'main/index.html', context)


login_required()


def results(request):
    if request.user.is_superuser:
        current_user = AditionalUserInfo.objects.get(username=str(request.user))
        unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
        exam_requests_count = ExamsRequests.objects.filter(status='new').count()
        exams = Exam.objects.all()
        user_exams = UsersExam.objects.all().order_by('retake')
        retake_count = user_exams.filter(retake=True).values_list('exam', flat=True).distinct()
        #retake_count = user_exams.filter(retake=True).values_list('exam').annotate(Count('exam', distinct=True))
        companys = AditionalUserInfo.objects.distinct('company').values_list('company')
        departments = AditionalUserInfo.objects.distinct('department').values_list('department')
        # SEARCH
        query = request.GET.get('search')
        if query:
            user_exams = UsersExam.objects.filter(Q(username__username__icontains=query))
        # FILTERS
        filter_exam = request.GET.get('filter_exam')
        filter_status = request.GET.get('filter_status')
        filter_retake = request.GET.getlist('retake')
        filter_company = request.GET.get('company')
        filter_department = request.GET.get('department')
        if filter_exam is not None:
            user_exams = user_exams.filter(exam_id=filter_exam)
            filter_exam = Exam.objects.get(pk=filter_exam).name
        if filter_status is not None:
            user_exams = user_exams.filter(status=filter_status)
        if len(filter_retake) == 1:
            user_exams = user_exams.filter(retake=filter_retake[0])
        if filter_company is not None:
            user_exams = user_exams.filter(username__company=filter_company)
        if filter_department is not None:
            user_exams = user_exams.filter(username__department=filter_department)
        page_num = request.GET.get('page', 1)
        paginator = Paginator(user_exams, 10)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        wrong_answers = IncorrectAnswers.objects.all()
        context = {
            'user_exams': page_obj,
            'wrong_answers': wrong_answers,
            'exams': exams,
            'departments': departments,
            'companys': companys,
            'filter_exam': filter_exam,
            'filter_status': filter_status,
            'filter_retake': filter_retake,
            'filter_company': filter_company,
            'filter_department': filter_department,
            'unread_notifications': unread_notifications,
            'exam_requests_count': exam_requests_count
        }

        if request.method == "POST" and user_exams:
            lines = []
            headers = [
                'Користувач', 'Співробітник', 'Підприємство', 'Департамент', 'Екзамен', 'Завершено', 'Статус',
                'Оцінка', 'Вірні відповіді', 'Не вірні відповіді', 'Перездача', 'Початок', 'Закінчення'
            ]
            lines.append(headers)
            for u in user_exams:
                incorrect_questions = IncorrectAnswers.objects.filter(username=u.username, exam=u.exam)
                incorrect_questions_to_csv = ''
                for incorrect_question in incorrect_questions:
                    incorrect_questions_to_csv = incorrect_questions_to_csv + incorrect_question.question + \
                                                 ': ' + incorrect_question.answer + '\n'
                lines.append([
                    u.username, u.username.get_full_name(), u.username.company, u.username.department, u.exam,
                    u.complete, u.status, u.score, str(u.correct_answer) + '/' + str(u.count_of_question),
                    incorrect_questions_to_csv, u.retake, u.start_time, u.end_time
                ])
            import csv
            base_dir = Path(__file__).resolve().parent.parent
            exports_dir = path.join(base_dir, "exports/report.csv")
            with open(exports_dir, 'w+', newline='', encoding='utf-8') as report:
                writer = csv.writer(report, delimiter=',')
                writer.writerows(lines)
                report.close()
            wrapper = FileWrapper(open(exports_dir, 'rb'))
            response = HttpResponse(wrapper, content_type='application/force-download')
            response['Content-Disposition'] = 'inline; filename=' + path.basename('./exports/report.csv')
            return response
        return render(request, 'main/results.html', context)
    else:
        return redirect(index)


@login_required()
def profile(request):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    notifications = Notification.objects.filter(user=current_user).order_by('-timestamp')
    unread_notifications = notifications.filter(is_read=False)
    read_notifications = notifications.filter(is_read=True)
    exams = UsersExam.objects.filter(username=current_user,).order_by('retake', 'exam')
    page_num = request.GET.get('page', 1)
    paginator = Paginator(exams, 4)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    complete_exams = exams.filter(complete=True, retake=False)
    count_complete_exams = len(complete_exams)
    retake_requests = ExamsRequests.objects.filter(username=current_user, status='new')
    retake_requests_ids = list(retake_requests.values_list('user_exam__exam', flat=True))
    score = 0
    for complete_exam in complete_exams:
        score += complete_exam.score
    if count_complete_exams != 0:
        score = score // count_complete_exams
    else:
        score = '-'
    context = {
        'exams': page_obj,
        'count_complete_exams': count_complete_exams,
        'score': score,
        'retake_requests': retake_requests_ids,
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications
    }
    return render(request, 'main/profile.html', context)


@login_required()
def aexams_requests(request):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    exam_requests_count = ExamsRequests.objects.filter(status='new').count()
    exams_requests = ExamsRequests.objects.all().order_by('-status')
    page_num = request.GET.get('page', 1)
    paginator = Paginator(exams_requests, 6)
    try:
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context = {
        'exams_requests': page_obj,
        'unread_notifications': unread_notifications,
        'exam_requests_count': exam_requests_count
    }
    return render(request, 'main/aexams_requests.html', context)


@login_required()
def exam_request_response(request):
    if request.method == 'POST':
        data = json.load(request)
        pk = data.get('pk')
        request_pk = data.get('request_pk')
        action = data.get('action')
        request = ExamsRequests.objects.get(pk=request_pk)
        messages = Message.objects.all()
        if request.status == 'new':
            if action == 'approve':
                user_exam = UsersExam.objects.get(pk=pk, complete=True, retake=False)
                user_exam.retake = True
                user_exam.save()
                request.status = 'approve'
                request.save()
                message = messages.get(name='request_approve').message
                html_message = f'<div class="alert alert-success" role="alert">{message}</div>'
                context = {
                    "html_message": html_message
                }
            elif action == 'deny':
                request = ExamsRequests.objects.get(pk=request_pk)
                request.status = 'deny'
                request.save()
                message = messages.get(name='request_deny').message
                html_message = f'<div class="alert alert-danger" role="alert">{message}</div>'
                context = {
                    "html_message": html_message
                }
        else:
            message = messages.get(name='request_already_processed').message
            html_message = f'<div class="alert alert-warning" role="alert">{message}</div>'
            context = {
                "html_message": html_message
            }
        return JsonResponse({'status': 'OK', 'context': context})
    else:
        pass


@login_required()
def exam_request(request):
    if request.method == 'POST':
        data = json.load(request)
        pk = data.get('pk')
        current_user = AditionalUserInfo.objects.get(username=str(request.user))
        current_exam = UsersExam.objects.get(username=current_user, pk=pk)
        messages = Message.objects.all()
        try:
            ExamsRequests.objects.get(username=current_user, user_exam=current_exam, status='new')
            message = messages.get(name='already_sent').message
            html_message = f'<div class="alert alert-warning" role="alert">{ message }</div>'
            context = {
                'html_message': html_message
            }
        except:
            try:
                ExamsRequests.objects.create(username=current_user, user_exam=current_exam, status='new')
                message = messages.get(name='sent').message
                html_message = f'<div class="alert alert-success" role="alert">{ message }</div>'
                context = {
                    'html_message': html_message
                }
            except:
                html_message = '<div class="alert alert-danger" role="alert">Тестування вже було перездано!</div>'
                context = {
                    'html_message': html_message
                }
        return JsonResponse({'status': 'OK', 'context': context}, safe=False)
    else:
        pass


@login_required
def dashboard(request):
    if request.user.is_superuser:
        current_user = AditionalUserInfo.objects.get(username=str(request.user))
        unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
        exam_requests_count = ExamsRequests.objects.filter(status='new').count()
        exams = Exam.objects.all()
        exams_count = Exam.objects.all().count()
        users_count = AditionalUserInfo.objects.all().count()
        start_date = datetime.today() - timedelta(days=6 * 30)
        end_date = datetime.today()
        user_trends = AditionalUserInfo.objects.annotate(
            month=TruncMonth('date_joined')
        ).filter(
            date_joined__gte=start_date,
            date_joined__lte=end_date
        ).values(
            'month'
        ).annotate(
            count=Count('id')
        )
        users_trend = []
        prev_month_users = 0
        for trend in user_trends:
            month = trend['month'].strftime("%b %Y")
            count = trend['count'] + prev_month_users
            prev_month_users = count
            users_trend.append({"y": count, "label": month})
        exam_trend = UsersExam.objects.filter(retake=False).values('exam').annotate(count=Count('exam'))
        exams_trend = []
        for trend in exam_trend:
            for exam in exams:
                if trend['exam'] == exam.pk:
                    trend_exam = exam.name
                    exams_trend.append({"y": trend['count'], "label": trend_exam})
        context = {
            'exams': exams,
            'exams_count': exams_count,
            'users_count': users_count,
            'main': True,
            'users_trend': users_trend,
            'exams_trend': exams_trend,
            'unread_notifications': unread_notifications,
            'exam_requests_count': exam_requests_count
        }
        return render(request, 'main/dashboards.html', context)
    else:
        return redirect(index)


@login_required
def dashboards(request, pk):
    if request.user.is_superuser:
        current_user = AditionalUserInfo.objects.get(username=str(request.user))
        unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
        exam_requests_count = ExamsRequests.objects.filter(status='new').count()
        exams = Exam.objects.all()
        companys = AditionalUserInfo.objects.distinct('company').values_list('company')
        departments = AditionalUserInfo.objects.distinct('department').values_list('department')
        # FILTER
        filter_company = request.GET.get('company')
        filter_department = request.GET.get('department')
        if filter_company is not None and filter_department is not None:
            users_count = int(
                AditionalUserInfo.objects.filter(company=filter_company, department=filter_department).count())
        elif filter_company is not None:
            users_count = int(AditionalUserInfo.objects.filter(company=filter_company).count())
        elif filter_department is not None:
            users_count = int(AditionalUserInfo.objects.filter(department=filter_department).count())
        else:
            users_count = ADInformation.objects.all().first().users_count
        exam = Exam.objects.get(pk=pk)
        # ACTIVE USERS
        active_users = UsersExam.objects.filter(exam_id=exam.pk, complete=False, retake=False)
        if filter_company is not None:
            active_users = active_users.filter(exam_id=exam.pk, complete=False, retake=False,
                                               username__company=filter_company)
        if filter_department is not None:
            active_users = active_users.filter(exam_id=exam.pk, complete=False, retake=False,
                                       username__department=filter_department)
        try:
            active_users_count = active_users.count()
            active_users_percent = round((active_users_count / users_count) * 100)
        except:
            active_users_count = 0
            active_users_percent = 0
        # -----------------------------------
        # COMPLETE USERS
        complete_users = UsersExam.objects.filter(exam_id=exam.pk, complete=True, retake=False)
        if filter_company is not None:
            complete_users = complete_users.filter(exam_id=exam.pk, complete=True, retake=False,
                                                   username__company=filter_company)
        if filter_department is not None:
            complete_users = complete_users.filter(exam_id=exam.pk, complete=True, retake=False,
                                                   username__department=filter_department)
        try:
            complete_users_count = complete_users.count()
            complete_users_percent = round((complete_users_count / users_count) * 100)
        except:
            complete_users_count = 0
            complete_users_percent = 0
        # -----------------------------------
        # NOT STARTED USERS
        try:
            not_start_users_count = users_count - active_users_count - complete_users_count
            not_start_users_percent = round((not_start_users_count / users_count) * 100)
        except:
            not_start_users_percent = 0
            not_start_users_count = 0
        # -----------------------------------
        # SUCCESS USERS
        success = UsersExam.objects.filter(exam_id=exam.pk, status='passed', complete=True,
                                            retake=False)
        if filter_company is not None:
            success.filter(exam_id=exam.pk, status='passed', complete=True,
                            retake=False, username__company=filter_company)
        if filter_department is not None:
            success.filter(exam_id=exam.pk, status='passed', complete=True,
                            retake=False, username__department=filter_department)
        try:
            success_count = success.count()
            success_percent = round((success_count / complete_users_count) * 100)
        except:
            success_percent = 0
            success_count = 0
            # -----------------------------------
        # NOT SUCCESS USER
        not_success = UsersExam.objects.filter(exam_id=exam.pk, status='not passed', complete=True, retake=False)
        if filter_company is not None:
            not_success = not_success.filter(exam_id=exam.pk, status='not passed', complete=True,
                                                retake=False, username__company=filter_company)
        if filter_department is not None:
            not_success = not_success.filter(exam_id=exam.pk, status='not passed', complete=True,
                                                retake=False, username__department=filter_department)
        try:
            not_success_count = not_success.count()
            not_success_percent = round((not_success_count / complete_users_count) * 100)
        except:
            not_success_percent = 0
            not_success_count = 0
        # -----------------------------------
        wrong_questions = IncorrectAnswers.objects.filter(exam_id=exam.pk)
        if filter_company is not None:
            wrong_questions = wrong_questions.filter(exam_id=exam.pk, username__company=filter_company)
        if filter_company is not None:
            wrong_questions = wrong_questions.filter(exam_id=exam.pk, username__department=filter_department)
        wrong_questions_list = []
        for wrong_question in wrong_questions:
            wrong_questions_list.append(wrong_question.question)
            wrong_questions_list = list(dict.fromkeys(wrong_questions_list))
        wrong_questions = []
        for wrong_question in wrong_questions_list:
            count = IncorrectAnswers.objects.filter(exam_id=exam.pk, question=wrong_question).count()
            wrong_questions.append([wrong_question, count])
        users_exam_companys = UsersExam.objects.filter(retake=False, exam_id=exam.pk, complete=True).order_by('username').values('username__company').annotate(count=Count('username__company'))
        dashboard_company_records = []
        for users_exam_company in users_exam_companys:
            username_company = users_exam_company['username__company']
            username_company_count = users_exam_company['count']
            dashboard_company_records.append({"y": username_company_count, "label": username_company})
        context = {
            'dashboard_company_records': dashboard_company_records,
            'users_count': users_count,
            'active_users_count': active_users_count,
            'active_users_percent': active_users_percent,
            'exam': exam,
            'exams': exams,
            'complete_users_count': complete_users_count,
            'complete_users_percent': complete_users_percent,
            'not_start_users_count': not_start_users_count,
            'not_start_users_percent': not_start_users_percent,
            'success_count': success_count,
            'success_percent': success_percent,
            'not_success_count': not_success_count,
            'not_success_percent': not_success_percent,
            'wrong_questions': wrong_questions,
            'companys': companys,
            'departments': departments,
            'filter_company': filter_company,
            'filter_department': filter_department,
            'unread_notifications': unread_notifications,
            'exam_requests_count': exam_requests_count
        }
        if request.method == "POST" and wrong_questions:
            headers = ['Питання', 'Кількість не вірних відповідей']
            wrong_questions.insert(0, headers)
            import csv
            base_dir = Path(__file__).resolve().parent.parent
            exports_dir = path.join(base_dir, "exports/report.csv")
            with open(exports_dir, 'w+', newline='', encoding='utf-8') as report:
                writer = csv.writer(report, delimiter=',')
                writer.writerows(wrong_questions)
                report.close()
            wrapper = FileWrapper(open(exports_dir, 'rb'))
            response = HttpResponse(wrapper, content_type='application/force-download')
            response['Content-Disposition'] = 'inline; filename=' + path.basename('./exports/report.csv')
            return response
        return render(request, 'main/dashboards.html', context)
    else:
        return redirect(index)


@login_required
def exams(request):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    exams = Exam.objects.filter(is_active=True)
    all_exams = UsersExam.objects.filter(username=current_user)
    retake_requests = ExamsRequests.objects.filter(username=current_user, status='new')
    retake_requests_ids = list(retake_requests.values_list('user_exam__exam', flat=True))
    complete_exams = all_exams.filter(complete=True, retake=False)
    retake_exams = all_exams.filter(complete=True, retake=True)
    retake_exams_ids = list(retake_exams.values_list('exam_id', flat=True))
    complete_exams_ids = list(complete_exams.values_list('exam_id', flat=True))
    not_complete_exams = all_exams.filter(username=current_user, complete=False)
    not_complete_exams_ids = list(not_complete_exams.values_list('exam_id', flat=True))
    context = {
        'exams': exams,
        'complete_exams': complete_exams,
        'complete_exams_ids': complete_exams_ids,
        'not_complete_exams_ids': not_complete_exams_ids,
        'retake_exams_ids': retake_exams_ids,
        'retake_requests': retake_requests_ids,
        'unread_notifications': unread_notifications
    }
    return render(request, 'main/exams.html', context)


@login_required
def exam_detail(request, pk):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    current_exam = get_object_or_404(Exam, pk=pk)
    try:
        complete_user_exam = UsersExam.objects.get(username=current_user, complete=True, exam=current_exam,
                                                   retake=False)
        complete_pk = complete_user_exam.exam_id
        if pk == complete_pk:
            return redirect(exams)
    except Exception as E:
        pass
    try:
        UsersExam.objects.get(username=current_user, exam=current_exam, complete=False)
    except:
        UsersExam.objects.create(username=current_user, exam=current_exam,
                                 status='active', start_time=datetime.now(),
                                 count_of_question=current_exam.count_of_question)
    questions = Question.objects.filter(exam=current_exam)
    context = {
        'exam': current_exam,
        'questions': questions,
        'unread_notifications': unread_notifications
    }
    if request.method == "POST":
        score_count = 0
        value_one_answer = 100 / current_exam.count_of_question
        for question in questions:
            if question.answer_count == 1:
                correct_answer = question.answers_as_list()
                correct_answer = correct_answer[0]
                current_answer = request.POST.get('answer_' + str(question.pk))
                if current_answer == correct_answer:
                    score_count += 1
                else:
                    IncorrectAnswers.objects.create(
                        username=current_user, exam=current_exam,
                        question=question, answer=current_answer)
            elif question.answer_count > 1:
                value_one_answers = 1 / question.answer_count
                corrects_answers = question.answers_as_list()
                corrects_answers = corrects_answers[:question.answer_count]
                current_answers = request.POST.getlist('answer_' + str(question.pk))
                for current_answer in current_answers:
                    if current_answer in corrects_answers:
                        score_count += value_one_answers
                    elif current_answer not in corrects_answers and score_count != 0:
                        score_count -= value_one_answers
                        IncorrectAnswers.objects.create(
                            username=current_user, exam=current_exam,
                            question=question, answer=current_answer
                        )
                    else:
                        IncorrectAnswers.objects.create(
                            username=current_user, exam=current_exam,
                            question=question, answer=current_answer
                        )
        score = score_count * value_one_answer
        score = round(score)
        complete = False
        update_record = UsersExam.objects.get(username=current_user, exam=current_exam, complete=False)
        if score_count >= current_exam.passing_score:
            complete = True
            update_record.status = 'passed'
        elif score_count < current_exam.passing_score:
            update_record.status = 'not passed'
        update_record.end_time = datetime.now()
        update_record.score = score
        update_record.complete = True
        update_record.correct_answer = score_count
        update_record.save()

        context = {
            'correct_answers': score_count,
            'count_answers': current_exam.count_of_question,
            'score': score,
            'exam': current_exam.name,
            'complete': complete,
            'unread_notifications': unread_notifications
        }
        return render(request, 'main/result.html', context)

    return render(request, 'main/exam.html', context)


def exam1(request, pk):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    current_exam = get_object_or_404(Exam, pk=pk)
    questions = Question.objects.filter(exam=current_exam)
    context = {
        'exam': current_exam,
        'questions': questions,
        'unread_notifications': unread_notifications
    }
    return render(request, 'main/exam.html', context)


@login_required
def aexams(request):
    if request.user.is_superuser:
        current_user = AditionalUserInfo.objects.get(username=str(request.user))
        unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
        exam_requests_count = ExamsRequests.objects.filter(status='new').count()
        exams = Exam.objects.all()
        context = {
            'exams': exams,
            'unread_notifications': unread_notifications,
            'exam_requests_count': exam_requests_count
        }
        return render(request, 'main/aexams.html', context)
    else:
        return redirect(index)


@login_required
def retake_exam_request(request, pk):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    current_exam = UsersExam.objects.get(username=current_user, pk=pk)
    messagess = Message.objects.all()
    try:
        ExamsRequests.objects.get(username=current_user, user_exam=current_exam, status='new')
        message = messagess.get(name='already_sent').message
        messages.warning(request, message)
    except:
        try:
            ExamsRequests.objects.create(username=current_user, user_exam=current_exam, status='new')
            message = messagess.get(name='sent')
            messages.success(request, message.message)
            notification = Notification(message=message,
                                        exam=current_exam.exam,
                                        user=current_user)
            notification.save()
        except:
            message = messagess.get(name='already_sent').message
            messages.warning(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def retake_exam_response(request, request_pk, user_exam_pk, action):
    retake_request = ExamsRequests.objects.get(pk=request_pk)
    messagess = Message.objects.all()
    if retake_request.status == 'new':
        if action == 'approve':
            user_exam = UsersExam.objects.get(pk=user_exam_pk, complete=True, retake=False)
            user_exam.retake = True
            user_exam.save()
            retake_request.status = 'approve'
            retake_request.save()
            message = messagess.get(name='request_approve')
            messages.success(request, message.message)
            notification = Notification(message=message,
                                        exam=retake_request.user_exam.exam,
                                        user=retake_request.username)
            notification.save()
        elif action == 'deny':
            retake_request.status = 'deny'
            retake_request.save()
            message = messagess.get(name='request_deny')
            messages.error(request, message.message)
            notification = Notification(message=message,
                                        exam = retake_request.user_exam.exam,
                                        user=retake_request.username)
            notification.save()
    else:
        message = messagess.get(name='request_already_processed').message
        messages.warning(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def staff_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        raise Http404()

    return wrapper


def read_all_notifications(request):
    current_user = AditionalUserInfo.objects.get(username=str(request.user))
    unread_notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-timestamp')
    for unread_notification in unread_notifications:
        unread_notification.is_read = True
        unread_notification.save()
    return redirect(profile)


def assignment_retake_exam(request, user_exam_pk):
    print(user_exam_pk)
    user_exam = UsersExam.objects.get(pk=user_exam_pk)
    user_exam.retake = True
    user_exam.save()
    messagess = Message.objects.all()
    message = messagess.get(name='assignment_retake_exam')
    messages.success(request, message.message + ' - ' + str(user_exam.username))
    notification = Notification(message=message,
                                exam=user_exam.exam,
                                user=user_exam.username)
    notification.save()
    return redirect(results)
