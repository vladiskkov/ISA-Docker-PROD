from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from parler.models import TranslatableModel, TranslatedFields


class AditionalUserInfo(AbstractUser):
    job_title = models.CharField(null=True, blank=True, max_length=255)
    department = models.CharField(null=True, blank=True, max_length=255)
    company = models.CharField(null=True, blank=True, max_length=255)
    manager = models.CharField(null=True, blank=True, max_length=255)


class ADInformation(models.Model):
    domain = models.CharField('Name', max_length=255, default='')
    users_count = models.IntegerField('Count of users', default='')

    def __str__(self):
        return self.domain


class Exam(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField('name', max_length=255), description=models.CharField('Опис', max_length=1000, default='Опис')
    )
    count_of_question = models.IntegerField('Кількість питань')
    passing_score = models.IntegerField(default=0)
    start_date = models.DateTimeField(verbose_name='Дата початку', default=datetime.datetime.now)
    end_date = models.DateTimeField(verbose_name='Дата закінчення', default=datetime.datetime.now)
    is_active = models.BooleanField(verbose_name='Тестування активно', default=False)
    create_date = models.DateField(default=datetime.datetime.today, blank=True)

    def __str__(self):
        return self.name


# Update status of EXAM
def update_is_active(sender, instance, **kwargs):
    if instance.end_date < timezone.now():
        instance.is_active = False
    elif instance.start_date >= timezone.now():
        instance.is_active = False
    else:
        instance.is_active = True


@receiver(pre_save, sender=Exam)
def exam_pre_save(sender, instance, **kwargs):
    update_is_active(sender, instance, **kwargs)


class Question(TranslatableModel):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='Екзамен')
    translations = TranslatedFields(
        question=models.CharField('Питання', max_length=1500),
        answer=models.CharField('Відповідь', max_length=1000)
    )
    answer_count = models.IntegerField('Кількість відповідей', default=1)

    def __str__(self):
        exam_question = str(self.question) + ': ' + str(self.exam)
        return exam_question

    def random_answers_as_list(self):
        import random
        answers = self.answer.split(';')
        random.shuffle(answers)
        return answers

    def random_answers_as_list_2(self):
        import random
        answers = self.answer.split(';')
        random.shuffle(answers)
        return answers

    def answers_as_list(self):
        return self.answer.split(';')


class UsersExam(models.Model):
    username = models.ForeignKey(AditionalUserInfo, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    status = models.CharField('Статус', max_length=255)
    complete = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    count_of_question = models.FloatField(blank=True, null=True)
    correct_answer = models.FloatField(blank=True, null=True)
    retake = models.BooleanField(default=False)

    def __str__(self):
        user_exam = str(self.username) + ': ' + str(self.exam) + ': ' + str(self.status)
        return user_exam


class IncorrectAnswers(models.Model):
    username = models.ForeignKey(AditionalUserInfo, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    def __str__(self):
        #title = str(self.username) + ': ' + str(self.exam)
        return self.question.question


class ExamsRequests(models.Model):
    username = models.ForeignKey(AditionalUserInfo, on_delete=models.CASCADE)
    user_exam = models.ForeignKey(UsersExam, on_delete=models.CASCADE)
    status = models.CharField(null=True, max_length=255)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    '''
    class Meta:
        unique_together = (("username", "user_exam"),)
    '''

    def __str__(self):
        return str(self.user_exam)


class Message(TranslatableModel):
    name = models.CharField(max_length=255)
    translations = TranslatedFields(
        message=models.CharField(max_length=255)
    )

    def __str__(self):
        return self.name


class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(AditionalUserInfo, on_delete=models.CASCADE)

    def __str__(self):
        title = self.message.message + ' [' + self.user.username + ']'
        return title
