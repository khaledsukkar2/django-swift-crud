from django.shortcuts import render, redirect
from django.views import View
from swift_crud.mixins import TemplateMixin, RedirectMixin, QuerysetMixin, FormMixin

class BaseView(View, TemplateMixin, RedirectMixin, QuerysetMixin, FormMixin):
    """
    BaseView class that provides basic CRUD operations for a Django model.
    It extends Django's View class and includes several mixins for additional functionalities.

    Attributes:
        model (django.db.models.Model): The model associated with this view.
        single_object_name (str): The context variable name for a single object.
        plural_object_name (str): The context variable name for a queryset of objects.
    """
    model = None
    single_object_name = None
    plural_object_name = None

    def get_model(self):
        """
        Returns the model associated with this view. Raises an error if the model is not set.

        Returns:
            model (django.db.models.Model): The model associated with this view.
        """
        if self.model is not None:
            return self.model
        raise ValueError("You must provide the model property.")

    def get_single_object_name(self):
        """
        Returns the context variable name for a single object.

        Returns:
            str: The context variable name for a single object.
        """
        return self.single_object_name or self.get_model()._meta.verbose_name

    def get_plural_object_name(self):
        """
        Returns the context variable name for a queryset of objects.

        Returns:
            str: The context variable name for a queryset of objects.
        """
        return self.plural_object_name or self.get_model()._meta.verbose_name_plural

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
        return render(request, self.get_template_name('list'), {self.get_plural_object_name(): queryset})

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
        return render(request, self.get_template_name('detail'), {self.get_single_object_name(): obj})

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
        return render(request, self.get_template_name('update'), {'form': form, self.get_single_object_name(): obj})

    def get_view_method(self, request, *args, **kwargs):
        """
        Determines the appropriate view method to handle the request based on the HTTP method and URL path.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            function: The view method to handle the request.
        """
        method = request.method.lower()
        path = request.path

        if method == 'get':
            if 'update' in path:
                return self.update_view
            elif 'create' in path:
                return self.create_view
            elif self.pk_url_kwarg in kwargs:
                return self.detail_view
            return self.list_view

        if method == 'post':
            if 'create' in path:
                return self.create_view
            elif 'update' in path:
                return self.update_view
            elif 'delete' in path:
                return self.delete_view

        if method == 'put' and 'update' in path:
            return self.update_view

        if method == 'delete' and 'delete' in path:
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
