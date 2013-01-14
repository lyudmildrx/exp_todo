
from django.contrib.admin import site
from todo import models

site.register(models.TodoItem)
