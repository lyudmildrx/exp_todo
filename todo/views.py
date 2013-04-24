from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from todo.models import TodoItem


def update(request, todoitem_id):
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
        return render(request, 'todo/detail.html', {
            'todoitem': note,
            'message': "You didn't update any field. Make a note of it!",
        })

    note.title = title
    note.order = order
    note.done = done
    note.save()

    return HttpResponseRedirect(reverse('todo:index'))


def create(request):
    note = TodoItem()
    title = request.POST['title']
    done = True if 'done' in request.POST.keys() else False
    try:
        order = int(request.POST['order'])
    except ValueError:
        order = None

    note.title = title
    note.order = order
    note.done = done
    note.save()

    return HttpResponseRedirect(reverse('todo:index'))


def delete(request, todoitem_id):
    note = get_object_or_404(TodoItem, pk=todoitem_id)
    note.delete()

    return HttpResponseRedirect(reverse('todo:index'))


def do(request, todoitem_id):
    note = get_object_or_404(TodoItem, pk=todoitem_id)
    note.done = True
    note.save()

    return HttpResponseRedirect(reverse('todo:index'))
