from django.db import models


class TodoList(models.Model):
    title = models.TextField()
    description = models.TextField()

    def to_json(self):
        """
            Prepare structure to be serialized as json
        """
        return {
            'title': self.title,
            'description': self.order,
        }
        


class TodoItem(models.Model):
    """
    Basic todo item

    It has a `title`, an `order` and can be marked as `done`
    """
    todolist = models.ForeignKey(TodoList)
    title = models.TextField()
    order = models.IntegerField(blank=True, null=True)
    done = models.BooleanField(default=False)

    def __repr__(self):
        return '<TodoItem %s>' % (self.title[:60].encode('utf-8'))

    def __unicode__(self):
        return self.title

    def to_json(self):
        """
            Prepare structure to be serialized as json
        """
        return {
            'title': self.title,
            'order': self.order,
            'done': self.done
        }
