# encoding: utf-8

import logging
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import json
from todo.views import TodoList, TodoItem

logger = logging.getLogger(__name__)


@login_required
def handle_rest_call(request, method, *args, **kwargs):
    # Determine serializer
    if 'fmt' in kwargs.keys():
        fmt = kwargs['fmt']
        if fmt.upper() == 'TO_JSON':
            serializer = 'to_json'
        elif fmt.upper() == 'TO_XML':
            serializer = 'to_xml'
        else:
            return HttpResponseBadRequest('')

    # Determine method
    if method.upper() == 'GET':
        qset = TodoList.objects.filter(Q(owner__id=request.user.id) |
                                       Q(shared_with=request.user) ).order_by('title')
        sset = ',\n'.join([getattr(_, serializer)() for _ in qset])

        return HttpResponse('kura_mi_qnko' + sset)

    elif method.upper() == 'POST':
        new_list = TodoList()
        new_list.owner = request.user
        data = json.load(raw_post_data)
        new_list.title = data['title']
        new_list.description = data['description']
        new_list.save()

        return HttpResponse(getattr(new_list, serializer)())

    elif method.upper() == 'PUT':
        pass
        return HttpResponse('')

    elif method.upper() == 'DELETE':
        if 'id' not in kwargs.keys():
            return HttpResponseBadRequest('')

        todolist_id = kwargs['id']
        latelist = get_object_or_404(TodoList, pk=todolist_id)
        latelist.delete()

        return HttpResponse(getattr(latelist, serializer)())
