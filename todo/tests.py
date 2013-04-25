"""
Defines test routines for todo application.

Tests are based on nose framework.
"""

import nose.tools as ntools
from django.test.client import Client
from django.core.urlresolvers import reverse
from todo.models import TodoItem, TodoList


def create_list(title, description, container=None):
    """
    """
    new_list = TodoList(title=title, description=description)

    if container is not None:
        new_list.save()
        container.append(new_list.id)

    return new_list


def create_todo(todolist, title, order, done, container=None):
    """
        Create a TodoItem with given values.
        If container is passed, the item is saved and id is appended to container.
    """
    item = TodoItem(
        todolist = todolist,
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
        dummy_list = create_list('Dummy', '4 Beerations per minute')
        item = create_todo(dummy_list, 'the title', 2, False)
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

        TestTodoViews.list_ids = []
        TestTodoViews.item_ids = []
        drink_list = create_list('Drink', 'Drink related', TestTodoViews.list_ids)
        create_todo(drink_list, 'Have no fear', 13, True, TestTodoViews.item_ids)
        create_todo(drink_list, 'but running out of beer', 12, False, TestTodoViews.item_ids)
        eat_list = create_list('Eat', 'About eating', TestTodoViews.list_ids)
        create_todo(eat_list, 'Have fear', 13, True, TestTodoViews.item_ids)
        create_todo(eat_list, 'only about beer', 12, False, TestTodoViews.item_ids)

    @classmethod
    def teardown_class(cls):
        """
            Test teardown
        """
        TodoList.objects.filter(pk__in=TestTodoViews.list_ids).delete()

    def test_list_index(self):
        """
        * The home page should now display every TODO list in the system. It should also provide the functionalities
          to create and delete new lists.
        
        * For each list add a counter to display the number of TODO items it contains.
        
        * Upon clicking on a list, every item in it should be displayed.
        """
        response = self.client.get(reverse('todo:list_index'))
        ntools.assert_equal(response.status_code, 200)
        lists = TodoList.objects.all()
        res_ids = [_.id for _ in response.context['todolists']]
        loc_ids = [_.id for _ in lists]
        ntools.assert_list_equal(res_ids, loc_ids)
        ntools.assert_in(reverse('todo:list_create'), response.content)

        detail_urls = [reverse('todo:item_index', args=(_,)) for _ in res_ids]
        for _ in detail_urls:
            ntools.assert_in(_, response.content)

        delete_urls = [reverse('todo:list_delete', args=(_,)) for _ in res_ids]
        for _ in delete_urls:
            ntools.assert_in(_, response.content)


    def test_list_create_delete(self):
        response = self.client.post(
                        reverse('todo:list_create'),
                        {'title': 'Delete this soon',
                         'description': 'Soonz',},
                    )
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_not_equal(lists, [])

        curr_list = lists.pop(0)
        response = self.client.post(reverse('todo:list_delete', args=(curr_list.id,)))
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(lists, [])
        
               

    def test_item_index(self):
        """
            Tests for:
            * Implement a main page where all TODO Items can be listed
            * On the same page add the possibility to create a TODO item. As soon as the new item is added the list should be refreshed.
            * Along side each TODO item, add a button so the item can be deleted.
            * Along side each TODO item, add a button to mark the todo item as done.
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        list_id = TestTodoViews.list_ids[0]
        response = self.client.get(reverse('todo:item_index', args=(list_id,)))
        ntools.assert_equal(response.status_code, 200)
        curr_list = TodoList.objects.get(pk=list_id)
        items = curr_list.todoitem_set.all()
        res_ids = [item.id for item in response.context['todos']]
        loc_ids = [item.id for item in items]
        ntools.assert_list_equal(res_ids, loc_ids)
        ntools.assert_in(reverse('todo:item_create', args=(list_id,)), response.content)

        detail_urls = [reverse('todo:item_detail', args=(_,)) for _ in res_ids]
        for _ in detail_urls:
            ntools.assert_in(_, response.content)

        delete_urls = [reverse('todo:item_delete', args=(_,)) for _ in res_ids]
        for _ in delete_urls:
            ntools.assert_in(_, response.content)

        do_urls = [reverse('todo:item_do', args=(_,)) for _ in res_ids]
        for _ in do_urls:
            ntools.assert_in(_, response.content)

    def test_item_details(self):
        """
            Tests for:
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        item = TodoItem.objects.filter(title='Have no fear')[0]
        response = self.client.get(reverse('todo:item_detail', args=(item.id,)))
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in(reverse('todo:item_update', args=(item.id,)), response.content)

    def test_item_do(self):
        """
            Do view should mark an item as done.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = self.client.post(reverse('todo:item_do', args=(item.id,)))
        ntools.assert_equal(response.status_code, 302)

        item = TodoItem.objects.get(pk=item.id)
        ntools.assert_equal(item.done, True)

    def test_item_update(self):
        """
            Update view should update values in the db.
            Update view should not generate a db query if item is not changed.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = self.client.post(
                        reverse('todo:item_update', args=(item.id,)),
                        {'title': item.title,
                         'order': item.order,
                         'done': item.done,},
                    )
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in('Make a note of it', response.content)

        response = self.client.post(
                        reverse('todo:item_update', args=(item.id,)),
                        {'title': 'new_title',
                         'order': 100,
                         'done': True,},
                    )
        item = TodoItem.objects.get(pk=item.id)
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(item.title, 'new_title')
        ntools.assert_equal(item.order, 100)
        ntools.assert_equal(item.done, True)

    def test_item_create_delete(self):
        """
            Creation and deletion of todoitems.
        """
        response = self.client.post(
                        reverse('todo:item_create', args=(TestTodoViews.list_ids[0],)),
                        {'title': 'Delete this todo note soon',
                         'order': 1,
                         'done': False,},
                    )
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_not_equal(items, [])

        item = items.pop(0)
        response = self.client.post(reverse('todo:item_delete', args=(item.id,)))
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(items, [])

