from django.http import HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from todo.models import TodoItem, TodoList
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext
from django.db.models import Q


# Will introduce at least one more DB query
#class owns_or_shared():
class _Owns():
    """
        Decorator for views.
        Checks for ownership.
    """
    def __init__(self, fn, or_shared=False):
        self.fn = fn
        self.or_shared = or_shared

    def __call__(self, request, **kwargs):
        if 'todolist_id' in kwargs.keys():
            todolist_id = kwargs['todolist_id']
        elif 'todoitem_id' in kwargs.keys():
            todoitem = get_object_or_404(TodoItem, pk=kwargs['todoitem_id'])
            kwargs['todoitem'] = todoitem
            todolist_id = todoitem.todolist.id
        else:
            # Nothing to own, lets see what you are doing
            return self.fn(request, **kwargs)

        todolist = get_object_or_404(TodoList, pk=todolist_id)
        kwargs['todolist'] = todolist
        if todolist.owner == request.user or \
          (self.or_shared and request.user in todolist.shared_with.all()):
            return self.fn(request, **kwargs)
        else:
            return HttpResponseRedirect(reverse('todo:permitions_denied'))


def owns(function=None, or_shared=False):
    if function:
        return _Owns(function)
    else:
        def wrapper(function):
            return _Owns(function, or_shared)

        return wrapper


@login_required
@require_GET
def list_index(request):
    qset = TodoList.objects.filter(Q(owner__id=request.user.id) |
                                   Q(shared_with=request.user) ).order_by('title')
    cont = RequestContext(request, {'todolists': qset})

    return render(request,
                  template_name = 'todo/list_index.html',
                  context_instance = cont)


@login_required
@require_POST
@owns
def list_create(request, **kwargs):
    new_list = TodoList()
    new_list.owner = request.user
    new_list.title = request.POST['title']
    new_list.description = request.POST['description']
    new_list.save()

    return HttpResponseRedirect(reverse('todo:list_index'))


@login_required
@require_POST
@owns
def list_delete(request, todolist_id, **kwargs):
    # Delete all items in list first
    if 'todolist' in kwargs.keys():
        latelist = kwargs['todolist']
    else:
        latelist = get_object_or_404(TodoList, pk=todolist_id)
    latelist.delete()

    return HttpResponseRedirect(reverse('todo:list_index'))


@login_required
@require_POST
@owns
def list_share(request, todolist_id, **kwargs):
    uid = int(request.POST['userid'])
    if uid == request.user.id:
        return HttpResponseRedirect(reverse('todo:list_index'))

    if 'todolist' in kwargs.keys():
        to_share = kwargs['todolist']
    else:
        to_share = get_object_or_404(TodoList, pk=todolist_id)

    if uid in [_.id for _ in to_share.shared_with.all()]:
        to_share.shared_with.remove(uid)
    else:
        to_share.shared_with.add(uid)
    to_share.save()

    return HttpResponseRedirect(reverse('todo:list_index'))


@login_required
@require_GET
@owns(or_shared=True)
def item_index(request, todolist_id, **kwargs):
    if 'todolist' in kwargs.keys():
        curr_list = kwargs['todolist']
    else:
        curr_list = get_object_or_404(TodoList, pk=todolist_id)
    todos = curr_list.todoitem_set.all()
    context = {'todos': todos, 'todolist': curr_list}

    return render(request, 'todo/item_index.html', context)


@login_required
@require_POST
@owns
def item_update(request, todoitem_id, **kwargs):
    if 'todoitem' in kwargs.keys():
        note = kwargs['todoitem']
    else:
        note = get_object_or_404(TodoItem, pk=todoitem_id)
    title = request.POST['title']
    done = True if 'done' in request.POST.keys() else False
    try:
        order = int(request.POST['order'])
    except ValueError:
        order = None

    if all([getattr(note, field) == locals()[field] \
            for field in ['title', 'order', 'done']]):
        # Redisplay the todoitem update form.
        return render(request, 'todo/item_detail.html', {
            'todoitem': note,
            'message': "You didn't update any field. Make a note of it!",
        })

    note.title = title
    note.order = order
    note.done = done
    note.save()

    return HttpResponseRedirect(reverse('todo:item_index', args=(note.todolist.id,)))


@login_required
@require_POST
@owns
def item_create(request, todolist_id, **kwargs):
    if 'todolist' in kwargs.keys():
        curr_list = kwargs['todolist']
    else:
        curr_list = get_object_or_404(TodoList, pk=todolist_id)
    note = TodoItem()
    title = request.POST['title']
    done = True if 'done' in request.POST.keys() else False
    try:
        order = int(request.POST['order'])
    except ValueError:
        order = None

    note.todolist = curr_list
    note.title = title
    note.order = order
    note.done = done
    note.save()

    return HttpResponseRedirect(reverse('todo:item_index', args=(todolist_id,)))


@login_required
@require_POST
@owns
def item_delete(request, todoitem_id, **kwargs):
    if 'todoitem' in kwargs.keys():
        note = kwargs['todoitem']
    else:
        note = get_object_or_404(TodoItem, pk=todoitem_id)
    list_id = note.todolist.id
    note.delete()

    return HttpResponseRedirect(reverse('todo:item_index', args=(list_id,)))


@login_required
@require_POST
@owns(or_shared=True)
def item_do(request, todoitem_id, **kwargs):
    if 'todoitem' in kwargs.keys():
        note = kwargs['todoitem']
    else:
        note = get_object_or_404(TodoItem, pk=todoitem_id)
    note.done = True
    note.save()

    return HttpResponseRedirect(reverse('todo:item_index', args=(note.todolist.id,)))
