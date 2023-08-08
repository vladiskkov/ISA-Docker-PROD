from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from parler.admin import TranslatableAdmin
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from os import environ


@admin.action(description='Update AD Azure user count')
def update_ad_info(modeladmin, request, queryset):
    os.environ["HTTPS_PROXY"] = HTTPS_PROXY
    credential = ClientSecretCredential(
            tenant_id=os.environ.get("TENANT_ID", "ea631a26-6dd8-4571-a85f-ebeda50d5724"), 
            client_secret=os.environ.get("CLIENT_SECRET", "iQj8Q~TXZx~KWG.zIk_osGDT91Wq2pkDA2KcTa2_"),
            client_id=os.environ.get("CLIENT_ID", "7444c7da-fe5b-4894-8348-702227048844")
    )
    client = GraphClient(credential=credential)
    # result = client.get('/users/' + str(user), params={'$select': 'department, jobTitle, onPremisesDistinguishedName'})
    results = client.get('/users/', params={'$select': 'displayName'})
    results = results.json()
    users_count = len(results['value'])
    queryset.update(users_count=int(users_count))


class ADInformationAdmin(admin.ModelAdmin):
    actions = [update_ad_info]


admin.site.register(ADInformation, ADInformationAdmin)
admin.site.register(Exam, TranslatableAdmin)
admin.site.register(Question, TranslatableAdmin)
admin.site.register(UsersExam)
admin.site.register(IncorrectAnswers)
admin.site.register(ExamsRequests)
admin.site.register(Message, TranslatableAdmin)
admin.site.register(Notification)


# Add fields to custom User model
fields = list(UserAdmin.fieldsets)
fields[1] = ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'job_title', 'department', 'manager', 'company')})
UserAdmin.fieldsets = tuple(fields)

admin.site.register(AditionalUserInfo, UserAdmin)
