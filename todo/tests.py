"""
Defines test routines for todo application.

Tests are based on nose framework.
"""

import nose.tools as ntools
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from todo.models import TodoItem, TodoList
from django.db.models import Q

from tastypie.test import ResourceTestCase

import code


def create_list(owner, title, description, container=None):
    """
        Create and return a TodoList with given values.
        If container is passed, the item is saved and id is appended to container.
    """
    new_list = TodoList(owner=owner, title=title, description=description)

    if container is not None:
        new_list.save()
        container.append(new_list.id)

    return new_list


def create_todo(todolist, title, order, done, container=None):
    """
        Create and return a TodoItem with given values.
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


class HelpTest():
    """
        Better namespace than globals
    """
    def __init__(self):
        self.client = Client()
        self.user_ids = []
        self.list_ids = []
        self.item_ids = []


def setup_module():
    """
        Populate DB and save ids.
    """
    global helper
    helper = HelpTest()

    # Create users
    helper.u1 = User.objects.create_user('john', 'void@void.com', '123456')
    helper.u2 = User.objects.create_user('johny', 'void@voider.com', 'A12345')
    helper.u3 = User.objects.create_user('johnier', 'void@voidest.com', 'B12345')
    helper.u1.save()
    helper.u2.save()
    helper.u3.save()
    helper.user_ids += [helper.u1.id, helper.u2.id, helper.u3.id]

    # Populate Lists and Items for users
    helper.u1l1 = create_list(helper.u1, 'Drink', 'Drink related', helper.list_ids)
    helper.u1l1i1 = create_todo(helper.u1l1, 'Have no fear', 13, True, helper.item_ids)
    helper.u1l1i2 = create_todo(helper.u1l1, 'but running out of beer', 12, False, helper.item_ids)
    helper.u1l2 = create_list(helper.u1, 'Eat', 'About eating', helper.list_ids)
    helper.u1l2i1 = create_todo(helper.u1l2, 'Have fear', 13, True, helper.item_ids)
    helper.u1l2i2 = create_todo(helper.u1l2, 'only about beer', 12, False, helper.item_ids)
    helper.u2l1 = create_list(helper.u2, 'Study', 'Slack related', helper.list_ids)
    helper.u2l1i1 = create_todo(helper.u2l1, 'Have a beer', 22, True, helper.item_ids)
    helper.u2l1i2 = create_todo(helper.u2l1, 'Irrigated exam == taken exam', 21, False, helper.item_ids)
    helper.u2l2 = create_list(helper.u2, 'Learn', 'The teachings', helper.list_ids)
    helper.u2l2i1 = create_todo(helper.u2l2, 'of the old beer brewer', 22, True, helper.item_ids)
    helper.u2l2i2 = create_todo(helper.u2l2, 'and beyond', 21, False, helper.item_ids)

    # User 3 is for REST test
    helper.u3l1 = create_list(helper.u3, 'l1', 'l1', helper.list_ids)
    helper.u3l1i1 = create_todo(helper.u3l1, 'l1i1', 13, True, helper.item_ids)
    helper.u3l2i2 = create_todo(helper.u3l1, 'l1i2', 12, False, helper.item_ids)
    helper.u3l2 = create_list(helper.u3, 'l2', 'l2', helper.list_ids)
    helper.u3l2i1 = create_todo(helper.u3l2, 'l2i1', 13, True, helper.item_ids)
    helper.u3l2i2 = create_todo(helper.u3l2, 'l2i2', 12, False, helper.item_ids)

    helper.u1l1.shared_with.add(helper.u2)
    helper.u2l2.shared_with.add(helper.u1)


def teardown_module():
    """
        Restore DB to 'as found'.
    """
    global helper
    TodoList.objects.filter(pk__in=helper.list_ids).delete()
    User.objects.filter(pk__in=helper.user_ids).delete()


class TestTodoItem():
    def test_json(self):
        """
            Checking json serialization
        """
        dummy_list = create_list(helper.u1, 'Dummy', '4 Beerations per minute')
        item = create_todo(dummy_list, 'the title', 2, False)
        result = item.to_json()
        ntools.assert_equals(
            result,'{"title": "the title","order": "2","done": "False"}'
            )


class TestTodoViews():
    @classmethod
    def setup_class(cls):
        """
            Test setup
            Login
        """
        helper.client.login(username='john', password='123456') # helper.u1

    @classmethod
    def teardown_class(cls):
        """
            Test teardown
            Logout
        """
        helper.client.logout()

    def test_list_index(self):
        """
        * The home page should now display every TODO list in the system. It should also provide the functionalities
          to create and delete new lists.

        * For each list add a counter to display the number of TODO items it contains.

        * Upon clicking on a list, every item in it should be displayed.

        * Should show shared and owned lists only.

        * Users that do not own the list should not see any interface that lets them create
          or delete items. Upon clicking on one of these items, the user should be prompt
          with the items details, but should not be able to edit them.
        """
        response = helper.client.get(reverse('todo:list_index'))
        ntools.assert_equal(response.status_code, 200)
        lists = TodoList.objects.filter(
            Q(owner=helper.u1) |
            Q(shared_with=helper.u1))
        res_ids = [_.id for _ in response.context['todolists']]
        loc_ids = [_.id for _ in lists]
        res_ids.sort()
        loc_ids.sort()
        ntools.assert_list_equal(res_ids, loc_ids)
        ntools.assert_in(reverse('todo:list_create'), response.content)

        detail_urls = [reverse('todo:item_index', args=(_,)) for _ in res_ids]
        for _ in detail_urls:
            ntools.assert_in(_, response.content)

        owned = TodoList.objects.filter(owner=helper.u1)
        del_ids = [_.id for _ in owned]
        delete_urls = [reverse('todo:list_delete', args=(_,)) for _ in del_ids]
        for _ in delete_urls:
            ntools.assert_in(_, response.content)


    def test_list_create_delete(self):
        response = helper.client.post(
                        reverse('todo:list_create'),
                        {'title': 'Delete this soon',
                         'description': 'Soonz',},
                    )
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_not_equal(lists, [])

        curr_list = lists.pop(0)
        response = helper.client.post(reverse('todo:list_delete', args=(curr_list.id,)))
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(lists, [])

        # Delete a shared list
        response = helper.client.post(
                        reverse('todo:list_create'),
                        {'title': 'Delete this soon',
                         'description': 'Soonz',},
                    )
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_not_equal(lists, [])
        new_list = lists[0]
        new_list.shared_with.add(helper.u2)

        curr_list = lists.pop(0)
        response = helper.client.post(reverse('todo:list_delete', args=(curr_list.id,)))
        lists = list(TodoList.objects.filter(title='Delete this soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(lists, [])


    def item_index(self, list_id):
        """
            Tests for:
            * Implement a main page where all TODO Items can be listed
            * On the same page add the possibility to create a TODO item. As soon as the new item is added the list should be refreshed.
            * Along side each TODO item, add a button so the item can be deleted.
            * Along side each TODO item, add a button to mark the todo item as done.
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        response = helper.client.get(reverse('todo:item_index', args=(list_id,)))
        ntools.assert_equal(response.status_code, 200)
        curr_list = TodoList.objects.get(pk=list_id)
        items = curr_list.todoitem_set.all()
        res_ids = [item.id for item in response.context['todos']]
        loc_ids = [item.id for item in items]
        ntools.assert_list_equal(res_ids, loc_ids)
        if curr_list.owner.id == helper.u1.id:
            ntools.assert_in(reverse('todo:item_create', args=(list_id,)), response.content)

        detail_urls = [reverse('todo:item_detail', args=(_,)) for _ in res_ids]
        for _ in detail_urls:
            ntools.assert_in(_, response.content)

        delete_urls = [reverse('todo:item_delete', args=(_.id,)) for _ in items if _.todolist.owner.id == helper.u1.id]
        for _ in delete_urls:
            ntools.assert_in(_, response.content)

        do_urls = [reverse('todo:item_do', args=(_,)) for _ in res_ids]
        for _ in do_urls:
            ntools.assert_in(_, response.content)

    def test_item_indexes(self):
        self.item_index(helper.u1l1.id)
        self.item_index(helper.u2l2.id)

    def test_item_details(self):
        """
            Tests for:
            * When clicking an item, a page with said item's details should be display. The user should be able to edit the item's fields.
        """
        item = TodoItem.objects.filter(title='Have no fear')[0]
        response = helper.client.get(reverse('todo:item_detail', args=(item.id,)))
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in(reverse('todo:item_update', args=(item.id,)), response.content)

    def test_item_do(self):
        """
            Do view should mark an item as done.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = helper.client.post(reverse('todo:item_do', args=(item.id,)))
        ntools.assert_equal(response.status_code, 302)

        item = TodoItem.objects.get(pk=item.id)
        ntools.assert_equal(item.done, True)

    def test_item_update(self):
        """
            Update view should update values in the db.
            Update view should not generate a db query if item is not changed.
        """
        item = TodoItem.objects.filter(title='but running out of beer')[0]
        response = helper.client.post(
                        reverse('todo:item_update', args=(item.id,)),
                        {'title': item.title,
                         'order': item.order,
                         'done': item.done,},
                    )
        ntools.assert_equal(response.status_code, 200)
        ntools.assert_in('Make a note of it', response.content)

        response = helper.client.post(
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
        response = helper.client.post(
                        reverse('todo:item_create', args=(helper.list_ids[0],)),
                        {'title': 'Delete this todo note soon',
                         'order': 1,
                         'done': False,},
                    )
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_not_equal(items, [])

        item = items.pop(0)
        response = helper.client.post(reverse('todo:item_delete', args=(item.id,)))
        items = list(TodoItem.objects.filter(title='Delete this todo note soon'))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_equal(items, [])


class TestTodoPermitions():
    @classmethod
    def setup_class(cls):
        """
            Test setup
        """
        helper.client.login(username='johny', password='A12345') # helper.u2

    @classmethod
    def teardown_class(cls):
        """
            Test teardown
        """
        helper.client.logout()

    def test_sharing(self):
        """
            Test (un)share own lists
        """
        todolist = TodoList.objects.get(pk=helper.u2l1.id)
        ntools.assert_not_in(helper.u1.id, [_.id for _ in todolist.shared_with.all()])
        response = helper.client.post(
                        reverse('todo:list_share', args=(helper.u2l1.id,)),
                        {'userid': helper.u1.id})
        ntools.assert_equal(response.status_code, 302)
        todolist = TodoList.objects.get(pk=helper.u2l1.id)
        ntools.assert_in(helper.u1.id, [_.id for _ in todolist.shared_with.all()])

        # And again
        response = helper.client.post(
                        reverse('todo:list_share', args=(helper.u2l1.id,)),
                        {'userid': helper.u1.id,},
                    )
        ntools.assert_equal(response.status_code, 302)
        todolist = TodoList.objects.get(pk=helper.u2l1.id)
        ntools.assert_not_in(helper.u1.id, todolist.shared_with.all())

    def test_messing_with_anothers_notes(self):
        # Can not share anothers lists
        response = helper.client.post(
                        reverse('todo:list_share', args=(helper.u1l1.id,)),
                        {'userid': helper.u1.id,},
                    )
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_in(reverse('todo:permitions_denied'), response.serialize_headers())

        # Can not delete anothers lists
        response = helper.client.post(reverse('todo:list_delete', args=(helper.u1l1.id,)))
        ntools.assert_equal(response.status_code, 302)
        ntools.assert_in(reverse('todo:permitions_denied'), response.serialize_headers())

        # Can mark as done anothers lists
        item = TodoItem.objects.get(pk=helper.u1l1i1.id)
        item.done = False
        item.save()
        response = helper.client.post(reverse('todo:item_do', args=(helper.u1l1i1.id,)))
        ntools.assert_equal(response.status_code, 302)
        item = TodoItem.objects.get(pk=helper.u1l1i1.id)
        ntools.assert_equals(True, item.done)

        # Can not see datails of list if not shared with user
        response = helper.client.get(reverse('todo:item_index', args=(helper.u1l2.id,)))
        ntools.assert_equal(response.status_code, 302)
        item = TodoItem.objects.get(pk=helper.u1l1i1.id)
        ntools.assert_in(reverse('todo:permitions_denied'), response.serialize_headers())


# Would not use resourcetestcase for now
class TestREST(ResourceTestCase):
    @classmethod
    def setup_class(cls):
        """
            Test setup
        """
        helper.client.login(username='johnier', password='B12345') # helper.u3
        helper.json_data1 = '{"title": "Title from post data", "description": "Description from post data"}'
        helper.json_data2 = '{"title": "Title from put data","description": "Description from put data"}'
        helper.json_data3 = '{"todolists": [{"title": "Title from put data 1","description": "Description from put data 1"}, {"title": "Title from put data 2","description": "Description from put data 2"}]}'


    @classmethod
    def teardown_class(cls):
        """
            Test teardown
        """
        helper.client.logout()
        del helper.json_data1
        del helper.json_data2
        del helper.json_data3

    def test_schema(self):
        response = helper.client.get(
                         reverse('todo:tastypie_api:api_get_schema', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                         {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response), {
            "allowed_detail_http_methods": ["get", "post", "delete", "put"],
            "allowed_list_http_methods": ["get", "post", "delete", "put"],
            "default_format": "json",
            "default_limit": 20,
            "fields": {"description": {"blank": False,
                                        "default": "",
                                        "help_text": "Unicode string data. Ex: \"Hello World\"",
                                        "nullable": False,
                                        "readonly": False,
                                        "type": "string",
                                        "unique": False},
                                        "owner": {"blank": False,
                                        "default": "No default provided.",
                                        "help_text": "A single related resource. Can be either a URI or set of nested resource data.",
                                        "nullable": False,
                                        "readonly": False,
                                        "related_type": "to_one",
                                        "type": "related",
                                        "unique": False},
                                        "title": {"blank": False,
                                        "default": "",
                                        "help_text": "Unicode string data. Ex: \"Hello World\"",
                                        "nullable": False,
                                        "readonly": False,
                                        "type": "string",
                                        "unique": False
                                    }
                    }
        })

    def test_todolist_resource_gets_json(self):
        """
            Test TodoListResource endpoints with GET method
        """
        response = helper.client.get(
                         reverse('todo:tastypie_api:api_dispatch_list', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                         {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['todolists']), 2)
        self.assertEqual(self.deserialize(response)['todolists'][0], {
            u'owner': {u'username': u'johnier'},
            u'description': u'l1',
            u'title': u'l1'
        })
        self.assertEqual(self.deserialize(response)['todolists'][1], {
            u'owner': {u'username': u'johnier'},
            u'description': u'l2',
            u'title': u'l2'
        })

        response = helper.client.get(
                         reverse('todo:tastypie_api:api_get_multiple', 
                                  kwargs={'resource_name':'todolist',
                                         'api_name': 'v1',  
                                         'pk_list':str(helper.u3l1.id) + ';' + str(helper.u3l2.id)}),
                         {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidJSONResponse(response)
        self.assertEqual(len(self.deserialize(response)['todolists']), 2)
        self.assertEqual(self.deserialize(response)['todolists'][0], {
            u'owner': {u'username': u'johnier'},
            u'description': u'l1',
            u'title': u'l1'
        })
        self.assertEqual(self.deserialize(response)['todolists'][1], {
            u'owner': {u'username': u'johnier'},
            u'description': u'l2',
            u'title': u'l2'
        })

        response = helper.client.get(
                        reverse('todo:tastypie_api:api_dispatch_detail', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1','pk':helper.u3l1.id,}),
                        {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidJSONResponse(response)
        self.assertEqual(self.deserialize(response), {
            u'description': u'l1',
            u'owner': {u'username': u'johnier'},
            u'title': u'l1'
        })

    def test_todolist_resource_gets_xml(self):
        """
            Test TodoListResource endpoints with GET method
        """
        response = helper.client.get(
                         reverse('todo:tastypie_api:api_dispatch_list', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                         {'format':'xml',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidXMLResponse(response)

        response = helper.client.get(
                         reverse('todo:tastypie_api:api_get_multiple', 
                                  kwargs={'resource_name':'todolist',
                                         'api_name': 'v1',  
                                         'pk_list':str(helper.u3l1.id) + ';' + str(helper.u3l2.id)}),
                         {'format':'xml',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidXMLResponse(response)

        response = helper.client.get(
                        reverse('todo:tastypie_api:api_dispatch_detail', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1','pk':helper.u3l1.id,}),
                        {'format':'xml',}
                    )
        ntools.assert_equal(response.status_code, 200)
        self.assertValidXMLResponse(response)

    def test_todolist_resource_posts(self):
        """
            Test TodoListResource endpoints with GET method
        """
        response = helper.client.post(
                        reverse('todo:tastypie_api:api_dispatch_list', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                        data = helper.json_data1,
                        content_type=u'application/json'
                    )
        ntools.assert_equal(response.status_code, 201)
        query = TodoList.objects.filter(title='Title from post data')
        ntools.assert_not_equal(query, [])

    def test_todolist_resource_puts(self):
        """
            Test TodoListResource endpoints with GET method
        """
        response = helper.client.put(
                        reverse('todo:tastypie_api:api_dispatch_detail', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1', 'pk':helper.u3l1.id,}),
                        data = helper.json_data2,
                        content_type = u'application/json',
                    )
        ntools.assert_equal(response.status_code, 204)
        query = TodoList.objects.filter(title='Title from put data')
        ntools.assert_not_equal(query, [])

        response = helper.client.put(
                        reverse('todo:tastypie_api:api_dispatch_list', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                        data = helper.json_data3,
                        content_type = u'application/json',
                    )
        ntools.assert_equal(response.status_code, 204)
        query = TodoList.objects.filter(title='Title from put data 1')
        ntools.assert_not_equal(query, [])
        query = TodoList.objects.filter(title='Title from put data 2')
        ntools.assert_not_equal(query, [])

    def test_todolist_resource_deletes(self):
        """
            Test TodoListResource endpoints with GET method
        """
        response = helper.client.delete(
                        reverse('todo:tastypie_api:api_dispatch_detail', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1','pk':helper.u3l1.id,}),
                        {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 204)
        query = TodoList.objects.filter(pk=helper.u3l1.id)
        ntools.assert_equal(query.count(), 0)

        response = helper.client.delete(
                        reverse('todo:tastypie_api:api_dispatch_list', 
                                 kwargs={'resource_name':'todolist', 'api_name': 'v1',}),
                        {'format':'json',}
                    )
        ntools.assert_equal(response.status_code, 204)
        query = TodoList.objects.filter(owner=helper.u3)
        ntools.assert_equal(query.count(), 0)
