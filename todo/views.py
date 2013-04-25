from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from todo.models import TodoItem, TodoList
from django.views.generic import ListView


def list_create(request):
    new_list = TodoList()
    new_list.title = request.POST['title']
    new_list.description = request.POST['description']
    new_list.save()

    return HttpResponseRedirect(reverse('todo:list_index'))


def list_delete(request, todolist_id):
    # Delete all items in list first
    latelist = get_object_or_404(TodoList, pk=todolist_id)
    latelist.delete()

    return HttpResponseRedirect(reverse('todo:list_index'))


def item_index(request, todolist_id):
    todos = TodoItem.objects.filter(todolist=todolist_id).order_by('-order')
    curr_list = get_object_or_404(TodoList, pk=todolist_id)
    context = {'todos': todos, 'todolist': curr_list}
    return render(request, 'todo/item_index.html', context)


def item_update(request, todoitem_id):
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


def item_create(request, todolist_id):
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


def item_delete(request, todoitem_id):
    note = get_object_or_404(TodoItem, pk=todoitem_id)
    list_id = note.todolist.id
    note.delete()

    return HttpResponseRedirect(reverse('todo:item_index', args=(list_id,)))


def item_do(request, todoitem_id):
    note = get_object_or_404(TodoItem, pk=todoitem_id)
    note.done = True
    note.save()

    return HttpResponseRedirect(reverse('todo:item_index', args=(note.todolist.id,)))
