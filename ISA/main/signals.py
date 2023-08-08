from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def add_initial_data(sender, **kwargs):
    pass
    '''
    if sender.name == 'main':
        # Replace 'your_app_name' with the actual name of your Django app
        from django.core.management import call_command
        call_command('add_initial_values')
        
    '''
