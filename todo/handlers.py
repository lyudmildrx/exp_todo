import logging
from piston.handler import BaseHandler
from todo.models import TodoItem

logger = logging.getLogger(__name__)


class TodoItemHandler(BaseHandler):
    allow_methods = ('GET', )
    model = TodoItem
    fields = ('id', 'title', 'order', 'done', )

    def read(self, request, todoitem_id=None):
        base = TodoItem.objects
        if todoitem_id is None:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('returning all items, count: %s', base.count())
            return base.all()
        else:
            logger.debug('Returning item with id %s', todoitem_id)
            return base.get(pk=todoitem_id)
