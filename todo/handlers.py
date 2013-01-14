import logging
from piston.handler import BaseHandler
from piston.utils import rc
from todo.models import TodoItem

logger = logging.getLogger(__name__)


class TodoItemHandler(BaseHandler):
    model = TodoItem
    fields = ('id', 'title', 'order', 'done', )
