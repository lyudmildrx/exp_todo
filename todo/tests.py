"""
Defines test routines for todo application.

Tests are based on nose framework.
"""

import nose.tools as ntools
from django.test.client import Client
from django.core.urlresolvers import reverse
from todo.models import TodoItem


def create_todo(title, order, done, container=None):
    """
        Create a TodoItem with given values.
        If container is passed, the item is saved and id is appended to container.
    """
    item = TodoItem(
        title = title,
        order = order,
        done = done,
    )

    if container is not None:
        item.save()
        container.append(item.id)

    return item


class TestTodoItem():
    def test_json(self):
        """
            Checking json serialization
        """
        item = create_todo('the title', 2, False)
        result = item.to_json()
        ntools.assert_equals(
            result,
            {'title': 'the title',
             'order': 2,
             'done': False}
        )


class TestTodoViews():
    @classmethod
    def setup_class(cls):
        """
            Test setup
        """
        TestTodoViews.client = Client()

        TestTodoViews.ids = []
        create_todo('Have no fear', 13, True, TestTodoViews.ids)
        create_todo('but running out of beer', 12, False, TestTodoViews.ids)

    @classmethod
    def teardown_class(cls):
        """
            Test teardown
        """
        while TestTodoViews.ids:
            TodoItem.objects.get(pk=TestTodoViews.ids.pop()).delete()

    def test_index(self):
        """
            Tests for:
            * Implement a main page where all TODO Items can be listed
            * On the same page add the possibility to create a TODO item. As soon as the new item is added the list should be refreshed.
            * Along side each TODO item, add a button so the item can be deleted.
            * Along side each TODO item, add a button to mark the todo item as done.
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        response = self.client.get(reverse('todo:index'))
        ntools.assert_equal(response.status_code, 200)
        items = TodoItem.objects.all()
        res_ids = [item.id for item in response.context['todos']]
        loc_ids = [item.id for item in items]
        ntools.assert_list_equal(res_ids, loc_ids)
        ntools.assert_in(reverse('todo:create'), response.content)

        detail_urls = [reverse('todo:detail', args=(_,)) for _ in res_ids]
        for _ in detail_urls:
            ntools.assert_in(_, response.content)

        delete_urls = [reverse('todo:delete', args=(_,)) for _ in res_ids]
        for _ in delete_urls:
            ntools.assert_in(_, response.content)

        do_urls = [reverse('todo:do', args=(_,)) for _ in res_ids]
        for _ in do_urls:
            ntools.assert_in(_, response.content)
        

    def test_details(self):
        """
            Tests for:
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        item = TodoItem.objects.filter(title='Have no fear')[0]
        response = self.client.get(reverse('todo:detail', args=(item.id,)))
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in(reverse('todo:update', args=(item.id,)), response.content)

    def test_do(self):
        """
            Do view should mark an item as done.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = self.client.post(reverse('todo:do', args=(item.id,)))
        ntools.assert_equal(response.status_code, 302)

        item = TodoItem.objects.get(pk=item.id)
        ntools.assert_equal(item.done, True)

    def test_update(self):
        """
            Update view should update values in the db.
            Update view should not generate a db query if item is not changed.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = self.client.post(
                        reverse('todo:update', args=(item.id,)),
                        {'title': item.title,
                         'order': item.order,
                         'done': item.done,},
                    )
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in('Make a note of it', response.content)

        response = self.client.post(
                        reverse('todo:update', args=(item.id,)),
                        {'title': 'new_title',
                         'order': 100,
                         'done': True,},
                    )
        item = TodoItem.objects.get(pk=item.id)
        ntools.assert_equal(item.title, 'new_title')
        ntools.assert_equal(item.order, 100)
        ntools.assert_equal(item.done, True)

    def test_create_delete(self):
        """
            Creation and deletion of todoitems.
        """
        response = self.client.post(
                        reverse('todo:create'),
                        {'title': 'Delete this todo note soon',
                         'order': 1,
                         'done': False,},
                    )
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_not_equal(items, [])

        item = items.pop(0)
        response = self.client.post(reverse('todo:delete', args=(item.id,)))
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_equal(items, [])

