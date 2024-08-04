"""

This Module is designed to provide a flexible and efficient way to handle routing for CBVs in Django
applications which utilizing the SwiftCrud lib.

Contribute Points:
- also it needs urls cache, so it doesn't load the routers from the start every time
- It doesn't support Regular Expression
- also it doesn't support @action decorater (like DRF @action)

Usage example:
from swift_crud.routers import DefaultRouter

router = DefaultRouter()
router.register("Employees/", EmployeeView, "Employee")

urlpatterns = []

urlpatterns += router.urls
"""

from typing import Any

from django.urls import path
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from swift_crud.views import SwiftView


class BaseRouter:

    def __init__(self) -> None:
        self.registery = []
    
    def register(self, prefix: str, swift_view: SwiftView, basename: str | None):
        """
        Register a SwiftView instance with a specified prefix and basename in the router.  

        This method is the main method for the BaseRouter class and its subclasses.  
        It checks for the uniqueness of the provided prefix and basename before   
        registering the SwiftView. If either the prefix or basename is already   
        registered, an ImproperlyConfigured exception is raised.

        Parameters:  
        ----------
        prefix : str  
            The URL prefix to associate with the swift_view. If the prefix is not   
            blank and does not end with a '/', a '/' will be appended.  
        
        swift_view : SwiftView  
            The SwiftView instance to register. This view will handle requests   
            routed to the specified prefix.  

        basename : str | None  
            An optional unique identifier for the swift_view. If None, the   
            default basename will be generated using the `get_default_basename` method.
        
        Raises  
        ------
        ImproperlyConfigured  
            - If the provided `basename` is already registered, a message will indicate   
            that a unique basename is required.  
            
            - If the provided `prefix` is already registered, a message will indicate   
            that a unique prefix is required.
        
        Notes  
        -----
        - The prefix checking may be deprecated in future versions when regular expression support is
        added for more flexible routing mechanism.
        
        """

        # if the prefix is not blank and is not ended with /, add it
        if prefix and prefix[-1] != "/":
            prefix += "/"

        if basename is None:
            basename = self.get_default_basename(swift_view)
        
        redundency_status, error_type = self.is_already_registered(basename, prefix)
        if redundency_status == True and error_type == "basename":
            
            raise ImproperlyConfigured(
                f'Router with basename "{basename}" is already registered. '
                f'Please provide a unique basename to your swift view "{swift_view}"'
                )
        
        elif redundency_status == True and error_type == "prefix":

            raise ImproperlyConfigured(
                f'Router with prefix "{prefix}" is already registered. '
                f'Please provide a unique prefix to your swift view "{swift_view}"'
                )
        
        # no errors raised, go append them
        self.registery.append((prefix, swift_view, basename))

    def is_already_registered(self, new_basename: str, new_prefix: str) -> tuple[bool, str]:
        """
        Check if the provided `basename` and `prefix` are already registered.

        This method iterates through the existing registrations in the `registery` to   
        determine if the given prefix or basename has already been used. If either one   
        has been previously registered, the method will return a flag indicating the   
        presence of the issue along with the specific attribute that is causing the conflict.  

        Parameters  
        ----------  
        new_basename : str  
            The basename that is being checked for uniqueness in the router's registry basenames.
            This should be a unique identifier for a specific SwiftView instance.

        new_prefix : str  
            The prefix that is being checked for uniqueness in the router's registry prefixes.
            Also, this should be a unique identifier for a specific SwiftView instance.

        Returns  
        -------
        tuple[bool, str]  
        A tuple containing:  
            - bool: A flag indicating whether a conflict exists (True if there is a problem with either 
                    basename or prefix, False otherwise).
            - str: A string indicating the name of the attribute that caused the issue.   
                    It will return "prefix" if the conflict is with the new prefix, "basename"   
                    if the conflict is with the new basename, or an empty string if there   
                    are no conflicts.
        """
        for prefix, swift_view, basename in self.registery:

            # prefix conflict found
            if prefix == new_prefix:
                return True, "prefix"
            
            # basename conflict found
            elif basename == new_basename:
                return True, "basename"
        
        # no conflicts found
        return False, ""
    
    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the viewset.

        note: this method is available only withing Inherited class that implement it
        it isn't available at BaseRouter level
        """
        raise NotImplementedError('get_default_basename must be overridden')

    def get_urls(self):
        """
        Return a list of URL patterns, given the registered viewsets.

        note: this method is available only withing Inherited class that implement it
        it isn't available at BaseRouter level
        """
        raise NotImplementedError('get_urls must be overridden')


class DefaultRouter(BaseRouter):

    def __init__(self) -> None:
        super().__init__()

    def get_default_basename(self, viewset):
        """
        If `basename` is not specified, attempt to automatically determine
        it from the model specified in the view.
        """
        model_class: models.Model = getattr(viewset, 'model', None)

        assert model_class is not None, '`basename` argument not specified, and could ' \
            'not automatically determine the name from the CBV, as ' \
            'it does not have a `model` attribute.'

        # if model_class attr is available, return its lower name
        return model_class._meta.object_name.lower()
    
    def method_url_pattern_map(self, method: str,  pk_url_kwarg: str, prefix: str, basename: str) -> tuple[str, str]:
        """
        Generate the prefix and basename to be added to swift_view instance URL Pattern.

        This method constructs the prefix and basename based on the specified HTTP method, 
        the primary key URL keyword argument, a prefix for the route, and a basename for the   
        resource. It is designed to return standardized paths for common CRUD operations   
        such as listing, creating, updating, and deleting resources.

        Parameters  
        ----------
        - method : str  
            The HTTP method for which the URL pattern is being generated. Expected values   
            include 'list', 'create', 'detail', 'update', and 'delete'.
        
        - pk_url_kwarg: str
            The keyword argument used to represent the primary key in the URL pattern.
        
        - prefix: str
            The URL prefix under which the resource is registered. This prefix already include a trailing
            slash (/)
        
        - basename : str
        The base name used to create unique names for the associated views. This will   
        be suffixed appropriately based on the method being considered.
        """
        default_patterns = {
            'list': (f'{prefix}list/', f'{basename}_list'),
            'create': (f'{prefix}create/', f'{basename}_create'),
            'detail': (f'{prefix}<int:{pk_url_kwarg}>/', f'{basename}_detail'),
            'update': (f'{prefix}<int:{pk_url_kwarg}>/update/', f'{basename}_update'),
            'delete': (f'{prefix}<int:{pk_url_kwarg}>/delete/', f'{basename}_delete')
            }
        
        return default_patterns[method]
    
    def get_urls(self) -> list:
        """
        Generate a list of URL patterns for registered views.  

        This method constructs a list of URL patterns based on the registered views   
        and their corresponding allowed_views.
        The resulting list of URL patterns can be used in a Django project's URL configuration to enable
        routing to the relevant views.

        Returns  
        -------
        A list of URL pattern definitions, each represented as a `path` object.  
        Each entry in the list corresponds to a view action defined in `allowed_views`.

        Notes
        -----
        - This method assumes that the `registry` attribute has been populated with the necessary view
        information, including the URL prefix, view class, and basename.  
        - Each SwiftView class that doesn't define its `allowed_views` attr, it will have the full five
        operations [list, detail, delete, create, update]
        """

        assert self.registery != [], "you can't use this method directly," \
            "you have to use router.register(...) first then request urls by using: router.urls"
        
        routes = []

        for prefix, swift_view, basename in self.registery:

            # declaring the view and prl_url_kwarg to use when building url paths
            consumed_view, pk_url_kwarg = swift_view.as_view(), swift_view.pk_url_kwarg

            # looping on declared allowed view from the view class
            allowed_views = swift_view.allowed_views
            for method in allowed_views:
                route, name = self.method_url_pattern_map(method, pk_url_kwarg, prefix, basename.lower())
                
                routes.append(
                    path(route=route, view=consumed_view, name=name)
                    )
        
        return routes

    @property
    def urls(self) -> list[Any]: # todo: what will return (type hinting) change Any
        return self.get_urls()
