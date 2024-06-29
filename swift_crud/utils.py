from django.urls import path

def generate_crud_urls(view, custom_patterns=None):
    """
    Generate CRUD URL patterns for a given view and model.

    Args:
        view (BaseView): The view class to use for the CRUD operations.
        custom_patterns (dict): Optional custom URL patterns and names.

    Returns:
        list: A list of URL patterns.
    """
    try:
        model_name = view.model._meta.model_name
    except:
        raise ValueError("the model attribute is empty, please provide a valid model")
    # Default URL patterns
    default_patterns = {
        'list': ('', view.as_view(), f'{model_name}_list'),
        'add': ('create/', view.as_view(), f'{model_name}_create'),
        'detail': ('<int:pk>/', view.as_view(), f'{model_name}_detail'),
        'update': ('<int:pk>/update/', view.as_view(), f'{model_name}_update'),
        'delete': ('<int:pk>/delete/', view.as_view(), f'{model_name}_delete'),
    }

    # Override default patterns with custom patterns if provided
    if custom_patterns:
        default_patterns.update(custom_patterns)

    urlpatterns = [
        path(f'{pattern}', view, name=name)
        for key, (pattern, view, name) in default_patterns.items()
    ]

    return urlpatterns