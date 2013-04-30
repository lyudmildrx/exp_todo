import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from todo.models import TodoItem, TodoList
from django.db.models import Q

class Command(BaseCommand):
    """
        For each user export a csv file which lists the users TODO lists.

        Format:
         + 1st column -> the TODO's list title
         + 2nd column -> the TODO's list description
         + 3rd column -> how many items does the list contain
         + 4th column -> information regarding if the list is owned or shared.
    """
    args = 'work_dir <username username...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        work_dir = args[0]
        if os.path.exists(work_dir):
            if not os.path.isdir(work_dir):
                self.stdout.write('ERROR. Working directory "%s" not acceptable' % work_dir)
                raise SystemExit
        else:
            os.mkdir(work_dir)
            

        for username in args[1:]:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError('User with name "%s" does not exist' % username)

            qset = TodoList.objects.filter(Q(owner__id=user.id) |
                                           Q(shared_with=user) ).order_by('title')

            with open(os.path.join(work_dir, username), 'wb') as csvfile:
                todowriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                for titem in qset:
                    todowriter.writerow([
                        titem.title,
                        titem.description,
                        titem.todoitem_set.count(),
                        'Owned' if user.id == titem.owner.id else 'Shared'
                    ])
