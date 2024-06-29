from django.http import Http404
from django.shortcuts import  get_object_or_404
from django.template.loader import get_template, TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator

class TemplateMixin:
    # the path to the folder of your templates.
    template_folder = ""
    """
    provide the name of the method as key(list, update, create, detail, delete) and the value is the path,
    for example: list:'dir/mymodel_list.html'
    use it when you want to change the template name or the dir name.
    """
    custom_templates = {}

    def get_template_name(self, prefix: str):
        if not self.template_folder and not self.custom_templates:
            raise ValueError("You must provide either the template_folder or custom_templates attribute.")

        if prefix in self.custom_templates:
            return self.custom_templates[prefix]
        else:
            template_name = f'{self.template_folder}/{self.get_single_object_name()}_{prefix}.html'
            
        try:
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            
            raise FileNotFoundError(f"Template {template_name} not found, check your paths in custom_templates or in template_folder attributes.")

    def _get_app_name(self):
        """
        get the app name for the view where it defined
        """
        return self.get_model()._meta.app_label


class RedirectMixin:
    redirect_url = ""

    def get_redirect_url(self):
        if self.redirect_url:
            return self.redirect_url
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a redirect_url.")


class QuerysetMixin:
    queryset = None
    pk_url_kwarg = "pk"
    paginate_by = None

    def get_queryset(self, request, *args, **kwargs):
        if self.queryset is not None:
            return self.queryset
        return self.get_model().objects.all()

    def get_object(self,request, *args, **kwargs):
        queryset = self.get_queryset(request, *args, **kwargs)
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            return get_object_or_404(queryset, pk=pk)
        raise Http404("No object found. Please re-check your pk_url_kwarg attribute or query.")

    
    def get_paginated_query(self, request, *args, **kwargs):
        queryset = self.get_queryset(request ,*args, **kwargs)
        paginator = Paginator(queryset, self.paginate_by)
        page = request.GET.get('page', 1)
        return paginator.get_page(page)


class FormMixin:
    form_class = None

    def get_form_class(self):
        if not self.form_class:
             raise ValueError("You must provide the form attribute.")
        
        return self.form_class
    
    def form_valid(self, form):
        form.save()


    def form_invalid(self, form):
        print(form.errors)