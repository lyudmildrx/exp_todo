from django.contrib.auth.models import User
from todo.models import TodoList

from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, NamespacedModelResource
from tastypie import fields
from tastypie.cache import SimpleCache
from tastypie.authentication import SessionAuthentication
from tastypie.serializers import Serializer


class CustomAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        if bundle.request and hasattr(bundle.request, 'user'):
            object_list = object_list.filter(owner=bundle.request.user)
            return object_list
        else:
            return object_list.none()


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = []
        excludes = ['id', 'first_name', 'last_name', 'email', 'password', 'last_login',
                    'is_active', 'is_staff', 'is_superuser', 'date_joined', 'is_active',]
        include_resource_uri = False


class TodoListResource(NamespacedModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)

    class Meta:
        queryset = TodoList.objects.all()
        resource_name = 'todolist'
        excludes = ['id',]
#        authorization = CustomAuthorization()
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'delete', 'put',]
        cache = SimpleCache(timeout=10)
        default_format = 'json'
        include_resource_uri = False
        collection_name = 'todolists'
        authentication = SessionAuthentication()
        serializer = Serializer(formats=['json', 'xml'])

    def dehydrate(self, bundle):
        return bundle

    def alter_list_data_to_serialize(self, request, data_dict):
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])

        return data_dict

    # Just to be has it heres
    def get_object_list(self, request):
        return super(TodoListResource, self).get_object_list(request).filter(owner=request.user)

#    def apply_authorization_limits(self, request, object_list):
#        return object_list.filter(owner=request.user)

    def obj_create(self, bundle, **kwargs):
        return super(TodoListResource, self).obj_create(bundle, owner=bundle.request.user)


