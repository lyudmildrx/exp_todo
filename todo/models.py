from django.db import models
from django.contrib.auth.models import User


class TodoList(models.Model):
    title = models.TextField()
    description = models.TextField()
    owner = models.ForeignKey(User, related_name='owned_set')
    shared_with = models.ManyToManyField(User, related_name='shared_lists')

    def to_json(self):
        """
            Prepare structure to be serialized as json
        """
        return '{{"title": "{0}","description": "{1}"}}'.format(
                self.title,
                self.description,
            )

    def to_xml(self):
        """
            Prepare structure to be serialized as json
        """
        return '<xml>\n<title>{0}<\\title>\n<description>{1}<\description><\\xml>'.format(
                self.title,
                self.description,
            )


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
        return '{{\"title\": \"{0}\",\"order\": \"{1}\",\"done\": \"{2}\"}}'.format(
                self.title,
                self.order,
                self.done,
            )

    def to_xml(self):
        """
            Prepare structure to be serialized as json
        """
        return '<xml>\n<title>{0}<\\title>\n<order>{1}<\order>\n<done>{2}<\done><\\xml>'.format(
                self.title,
                self.order,
                self.done,
            )
