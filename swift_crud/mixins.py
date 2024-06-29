from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator

class TemplateMixin:
    """
    Mixin to handle template selection for views.
    
    Attributes:
        template_folder (str): Path to the folder containing templates.
        custom_templates (dict): Custom template paths mapped to view methods (list, update, create, detail, delete).
    """
    template_folder = ""
    custom_templates = {}

    def get_template_name(self, prefix: str):
        """
        Retrieve the appropriate template name based on the given prefix.
        
        Args:
            prefix (str): The prefix indicating the view type (list, update, create, detail, delete).

        Returns:
            str: The path to the template.

        Raises:
            ValueError: If neither template_folder nor custom_templates are provided.
            FileNotFoundError: If the specified template does not exist.
        """
        if not self.template_folder and not self.custom_templates:
            raise ValueError("You must provide either the template_folder or custom_templates attribute.")

        # Determine the template name based on custom_templates or template_folder
        template_name = self.custom_templates.get(prefix, f'{self.template_folder}/{self.get_single_object_name()}_{prefix}.html')
        
        try:
            # Check if the template exists
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            raise FileNotFoundError(f"Template {template_name} not found, check your paths in custom_templates or in template_folder attributes.")

    def _get_app_name(self):
        """
        Retrieve the app name for the view where it is defined.
        
        Returns:
            str: The app label.
        """
        return self.get_model()._meta.app_label


class RedirectMixin:
    """
    Mixin to handle redirections after form submissions.
    
    Attributes:
        redirect_url (str): The URL to redirect to.
    """
    redirect_url = ""

    def get_redirect_url(self):
        """
        Retrieve the URL to redirect to.
        
        Returns:
            str: The redirect URL.

        Raises:
            ImproperlyConfigured: If redirect_url is not provided.
        """
        if self.redirect_url:
            return self.redirect_url
        raise ImproperlyConfigured("No URL to redirect to. Provide a redirect_url.")


class QuerysetMixin:
    """
    Mixin to handle queryset retrieval and pagination.
    
    Attributes:
        queryset (QuerySet): The queryset to use.
        pk_url_kwarg (str): The URL keyword argument for the primary key.
        paginate_by (int): Number of items per page for pagination.
    """
    queryset = None
    pk_url_kwarg = "pk"
    paginate_by = None

    def get_queryset(self, request, *args, **kwargs):
        """
        Retrieve the queryset for the view.
        
        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: The queryset.
        """
        if self.queryset is not None:
            return self.queryset
        return self.get_model().objects.all()

    def get_object(self, request, *args, **kwargs):
        """
        Retrieve a single object from the queryset.
        
        Args:
            request (HttpRequest): The request object.

        Returns:
            Model: The retrieved object.

        Raises:
            Http404: If the object is not found.
        """
        queryset = self.get_queryset(request, *args, **kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            return get_object_or_404(queryset, pk=pk)
        raise Http404("No object found. Please re-check your pk_url_kwarg attribute or query.")

    def get_paginated_query(self, request, *args, **kwargs):
        """
        Retrieve the paginated queryset.
        
        Args:
            request (HttpRequest): The request object.

        Returns:
            Page: The paginated page of objects.
        """
        queryset = self.get_queryset(request, *args, **kwargs)
        paginator = Paginator(queryset, self.paginate_by)
        page = request.GET.get('page', 1)
        return paginator.get_page(page)


class FormMixin:
    """
    Mixin to handle form processing.
    
    Attributes:
        form_class (Form): The form class to use.
    """
    form_class = None

    def get_form_class(self):
        """
        Retrieve the form class.
        
        Returns:
            Form: The form class.

        Raises:
            ValueError: If form_class is not provided.
        """
        if not self.form_class:
            raise ValueError("You must provide the form_class attribute.")
        return self.form_class

    def form_valid(self, form):
        """
        Handle valid form submission.
        
        Args:
            form (Form): The valid form.
        """
        form.save()

    def form_invalid(self, form):
        """
        Handle invalid form submission.
        
        Args:
            form (Form): The invalid form.
        """
        # Log form errors for debugging
        print(form.errors)
