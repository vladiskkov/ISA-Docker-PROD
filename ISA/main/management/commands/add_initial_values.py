from django.core.management.base import BaseCommand
from main.models import Message, ADInformation


class Command(BaseCommand):
    # Adds initial values to models
    def handle(self, *args, **options):
        # Add messages
        initial_messages = [
            {'name': 'assignment_retake_exam'},
            {'name': 'already_sent'},
            {'name': 'sent'},
            {'name': 'request_approve'},
            {'name': 'request_deny'},
            {'name': 'request_already_processed'},
        ]

        for data in initial_messages:
            Message.objects.create(**data)

        # Add default AD information
        initial_ad_information = [
            {'domain': 'default', 'users_count': 1}
        ]
        for data in initial_ad_information:
            ADInformation.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Initial values added successfully!'))
