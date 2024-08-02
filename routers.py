"""
Python module that works together with allowed_views list to enable routers feature
main goal: provide a way to router requests to Django CBVs with multiple CRUD ops (like Viewsets in DRF)
it doesn't support Regular Expression (until now) (good point to contribute!)
also it doesn't support @action decorater (until now) (no need to see, good point to contribute)
also it needs urls cache, so it doesn't load the routers from the start every time

todo: write an example
example:

"""

from typing import Any

from django.urls import path
from django.core.exceptions import ImproperlyConfigured

from swift_crud.views import SwiftView

class BaseRouter:

    def __init__(self) -> None:
        self.registery = []
    
    def register(self, prefix: str, swift_view: SwiftView, basename: str | None):
        # todo: more handling for the prefix naming conventions

        # if the prefix not blank and not ended with /, add it
        if prefix and prefix[-1] != "/":
            prefix = prefix[:-1]

        if basename is None:
            basename = self.get_default_basename(swift_view)
        
        check_router_attrs = self.is_already_registered(basename, prefix)
        redundency_status, error_type = check_router_attrs[0], check_router_attrs[1]

        if redundency_status == True and error_type == "basename":
            
            raise ImproperlyConfigured(
                f'Router with basename "{basename}" is already registered. '
                f'Please provide a unique basename to your swift view "{swift_view}"'
                )
        
        # note: prefix checking maybe deperecated by time when adding Regular Expression
        elif redundency_status == True and error_type == "prefix":

            raise ImproperlyConfigured(
                f'Router with prefix "{prefix}" is already registered. '
                f'Please provide a unique prefix to your swift view "{swift_view}"'
                )
        
        # no errors raised, go append them
        self.registery.append((prefix, swift_view, basename))

    def is_already_registered(self, new_basename: str, new_prefix: str) -> tuple[bool, str]:
        """
        Check if `basename` and `prefix` are already registered
        """
        for prefix, swift_view, basename in self.registery:

            if prefix == new_prefix:
                return True, "prefix"
            
            elif basename == new_basename:
                return True, "basename"
        
        return False, ""
    
    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the viewset.
        """
        raise NotImplementedError('get_default_basename must be overridden')

    def get_urls(self):
        """
        Return a list of URL patterns, given the registered viewsets.
        """
        raise NotImplementedError('get_urls must be overridden')


class DefaultRouter(BaseRouter):
    # todo: this routes list to be used in future (cache urls feature)
    # routes = []
    
    def __init__(self) -> None:
        # need to find self.routes
        super().__init__()

    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the model specified in the view.
        """
        model_class = getattr(viewset, 'model', None)

        assert model_class is not None, '`basename` argument not specified, and could ' \
            'not automatically determine the name from the CBV, as ' \
            'it does not have a `model` attribute.'

        # if model_class attr is available, return its lower name
        return model_class._meta.object_name.lower()
    
    def method_url_pattern_map(self, method: str,  pk_url_kwarg: str, prefix: str, basename: str) -> tuple[str, str]:
        default_patterns = {
            'list': (f'{prefix}', f'{basename}_list'),
            'create': (f'{prefix}create/', f'{basename}_create'),
            'detail': (f'{prefix}<int:{pk_url_kwarg}>/', f'{basename}_detail'),
            'update': (f'{prefix}<int:{pk_url_kwarg}>/update/', f'{basename}_update'),
            'delete': (f'{prefix}<int:{pk_url_kwarg}>/delete/', f'{basename}_delete')
            }
        
        return default_patterns[method]
    
    def _get_urls(self) -> list:
        routes = []
        registered_routers = self.registery

        for prefix, swift_view, basename in registered_routers:

            view_allowed_methods = swift_view.allowed_views
            for method in view_allowed_methods:
                consumed_view = swift_view.as_view()
                pk_url_kwarg = swift_view.pk_url_kwarg

                route, name = self.method_url_pattern_map(method, pk_url_kwarg, prefix, basename.lower())
                built_path = path(route=route, view=consumed_view, name=name)

                routes.append(built_path)
        
        return routes

    @property
    def urls(self) -> list[Any]: # todo: what will return (type hinting)
        return self._get_urls()
