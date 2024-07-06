from django.shortcuts import render, redirect
from django.views import View
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

        method: str = request.method.lower()
        path: str = request.path 
        path_sections: list[str] = path.split("/")
        path_sections: list[str] = path_sections[1:-1]

        view_method_router = {
            "create": self.create_view,
            "update": self.update_view,
            "delete": self.delete_view,
            str(kwargs.get(self.pk_url_kwarg)): self.detail_view,
            path_sections[0]: self.list_view
        }

        if method == 'get' or method == "post":
            try:
                view_method = view_method_router.get(path_sections[-1])
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
