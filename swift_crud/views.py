from django.views import View
from django.shortcuts import render, redirect
from django.core.exceptions import ViewDoesNotExist

from swift_crud.mixins import TemplateMixin, RedirectMixin, QuerysetMixin, FormMixin


class SwiftView(View, TemplateMixin, RedirectMixin, QuerysetMixin, FormMixin):
    """
    SwiftView class that provides basic CRUD operations for a Django model.
    It extends Django's View class and includes several mixins for additional functionalities.

    Attributes:
        model (django.db.models.Model): The model associated with this view.
        verbose_name (str): The context variable name for a single object.
        verbose_name_plural (str): The context variable name for a queryset of objects.
    """
    model = None
    verbose_name = None
    verbose_name_plural = None

    # add new class attr
    allowed_views = ["detail", "list", "update", "create", "delete"]

    def get_model(self):
        """
        Returns the model associated with this view. Raises an error if the model is not set.

        Returns:
            model (django.db.models.Model): The model associated with this view.
        """
        if self.model is not None:
            return self.model
        raise ValueError("You must provide the model property.")

    def get_verbose_name(self):
        """
        Returns the context variable name for a single object.

        Returns:
            str: The context variable name for a single object.
        """
        return self.verbose_name or self.get_model()._meta.verbose_name

    def get_verbose_name_plural(self):
        """
        Returns the context variable name for a queryset of objects.

        Returns:
            str: The context variable name for a queryset of objects.
        """
        return self.verbose_name_plural or self.get_model()._meta.verbose_name_plural

    def list_view(self, request, *args, **kwargs):
        """
        Handles the list view of the model objects.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML page with a list of model objects.
        """
        queryset = self.get_queryset(request, *args, **kwargs)
        if self.paginate_by is not None:
            queryset = self.get_paginated_query(request, *args, **kwargs)
        return render(request, self.get_template_name('list'), {self.get_verbose_name_plural(): queryset})

    def detail_view(self, request, *args, **kwargs):
        """
        Handles the detail view of a single model object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML page with the details of a single model object.
        """
        obj = self.get_object(request, *args, **kwargs)
        return render(request, self.get_template_name('detail'), {self.get_verbose_name(): obj})

    def delete_view(self, request, *args, **kwargs):
        """
        Handles the deletion of a single model object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the specified URL after deletion.
        """
        obj = self.get_object(request, *args, **kwargs)
        obj.delete()
        return redirect(self.get_redirect_url())

    def create_view(self, request, *args, **kwargs):
        """
        Handles the creation of a new model object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML page with a form for creating a new model object.
            HttpResponseRedirect: Redirects to the specified URL after successful creation.
        """
        form_class = self.get_form_class()
        form = form_class(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            self.form_valid(form)
            return redirect(self.get_redirect_url())
        return render(request, self.get_template_name('create'), {'form': form})

    def update_view(self, request, *args, **kwargs):
        """
        Handles the update of an existing model object.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: Rendered HTML page with a form for updating the model object.
            HttpResponseRedirect: Redirects to the specified URL after successful update.
        """
        obj = self.get_object(request, *args, **kwargs)
        form_class = self.get_form_class()
        form = form_class(request.POST or None, instance=obj)
        if request.method == 'POST' and form.is_valid():
            self.form_valid(form)
            return redirect(self.get_redirect_url())
        return render(request, self.get_template_name('update'), {'form': form, self.get_verbose_name(): obj})

    def _allowed_views(self) -> set[str]:
        """
        Check allowed_methods by verifying these conditions:
        1] Standardize allowed_methods names to lowercase.
        2] Remove redundant view_methods names from allowed_methods.
        3] Filter out any strange or weird view_method names.

        Args:

        Returns:
            set of strings: the allowed view_methods names
        """
        # 1] initialize a set to guarantee non-redundent views (maybe user put 'list' twice)
        clear_views = set()

        # 2] compare between original views and user inputed views
        # we choose set to compare faster
        acceptable_views = {"detail", "list", "update", "create", "delete"}
        
        # 3] loop through each inputed view, then lower() it
        for view in self.allowed_views:
            view = view.lower()

            # 3.1] if view doesn't appear in acceptable views set, raise a ValidatonError
            if view not in acceptable_views:
                raise TypeError(
                    "%s is not a valid view name, Please ensure there are no spelling errors. "
                    "Allowed method names are: detail, list, update, create and delete" % view
                )
            
            # 3.2] if view in acceptable views, add it our clear_views set
            else:
                clear_views.add(view)
        
        # 4] return the final result
        return clear_views

    def get_view_method(self, request, *args, **kwargs):
        """
        Determines the appropriate view method to handle the request based on the HTTP method and URL path.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            callable: The view method to handle the request.
        """

        # to detect view_method from path faster, we split path
        # ex: /employees/9/update/ -> after .split("/"): ['', 'employees', '9', 'update', '']
        # then we slice the path_sections[1:-1], result: ['employees', '9', 'update']
        # then we check the path_sections[-1]

        # more examples on multiple methods:
        # /employees/9/delete/ -> .split("/"): ['employees', '9', 'delete'], path_sections[-1] will be 'delete'
        # /employees/9/create/ -> .split("/"): ['employees', '9', 'create'], path_sections[-1] will be 'create'
        # /employees/9/ -> .split("/"): ['employees', '9'], path_sections[-1] will be '9'
        # /employees/ -> .split("/"): ['employees'], path_sections[-1] will be 'employees'

        # list and get view_method_detector:
        # 1] get:
        # as we say: /employees/9/ -> .split("/"): ['employees', '9'], path_sections[-1] will be '9'
        # so we get the str() version of the pk
        # 2] list:
        # as we say: /employees/9/ -> .split("/"): ['employees', '9'], path_sections[-1] will be 'employees'
        # so we just check if there is no method to detect, and thus path_sections[0] == path_sections[1]

        # 1] first we get the http method from the request
        method: str = request.method.lower()

        # 2] then working with path to get view_method name
        path: str = request.path
        path_sections: list[str] = path.split("/")
        path_sections: list[str] = path_sections[1:-1]
        
        view_method_router = {
            "list": self.list_view,
            "create": self.create_view,
            "update": self.update_view,
            "delete": self.delete_view,
            str(kwargs.get(self.pk_url_kwarg)): self.detail_view
        }

        if method == 'get' or method == "post":
            try:
                view_method = view_method_router.get(path_sections[-1])
                
                # here we get the view_method name from the result of view_method_router
                # if the path_section[-1] is 'create' then the view_method will be self.create_view
                # here we take the name only (create_view in this example)
                # then splitting by '_'
                view_method_name = view_method.__name__.split("_")
                view_method_name = view_method_name[0]
                
                # 3] then we have to check if the view_method_name available in allowed_views list
                allowed_views = self._allowed_views()
                
                # 3.1] if it isn't in allowed views we raise validation error 
                if view_method_name not in allowed_views:
                    raise ViewDoesNotExist(
                        "you can't use %s view, the %s view isn't in allowed_views, "
                        "please double check the allowed_views list" % (view_method_name, view_method_name)
                    )
                
                # 3.2] else we return the view_method normally
                return view_method
            except Exception as e:
                raise e

        # note: maybe we need patch, not just put (for ajax)
        if method == 'put' and 'update' == path[-1]:
            return self.update_view

        if method == 'delete' and 'delete' == path[-1]:
            return self.delete_view

        return None

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the dispatch method to route the request to the appropriate view method.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The response generated by the appropriate view method.
        """
        view_method = self.get_view_method(request, *args, **kwargs)
        if view_method:
            return view_method(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
