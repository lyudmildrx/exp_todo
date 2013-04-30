import os
import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from todo.models import TodoItem, TodoList
from django.db.models import Q

class Command(BaseCommand):
    """
        For each TODO list export a csv file which lists the list's TODO items.

        Format:
         + 1st column -> the TODO item's title
         + 2nd column -> information regarding if the item is done or not.
    """
    args = 'work_dir <list_title list_title...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        work_dir = args[0]
        if os.path.exists(work_dir):
            if not os.path.isdir(work_dir):
                self.stdout.write('ERROR. Working directory "%s" not acceptable' % work_dir)
                raise SystemExit
        else:
            os.mkdir(work_dir)

        qset = TodoList.objects.filter(title__in=args[1:])
        for tlist in qset:
            with open(os.path.join(work_dir, tlist.title), 'wb') as csvfile:
                todowriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                nodeset = TodoItem.objects.filter(todolist=tlist)
                for titem in nodeset:
                    todowriter.writerow([
                        titem.title,
                        'Done' if titem.done else 'To do',
                    ])
