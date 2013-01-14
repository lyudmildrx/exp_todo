from django.db import models


class TodoItem(models.Model):
    """
    Basic todo item

    It has a `title`, an `order` and can be marked as `done`
    """

    title = models.TextField()
    order = models.IntegerField(blank=True, null=True)
    done = models.BooleanField(default=False)

    def __repr__(self):
        return '<TodoItem %s>' % (self.title[:60].encode('utf-8'))

    def __unicode__(self):
        return self.title

    def to_json(self):
        """Prepare structure to be serialized as json"""
        return {
            'title': self.title,
            'order': self.order,
            'done': self.done}
