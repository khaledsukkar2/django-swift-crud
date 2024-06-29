from django.urls import path

def generate_crud_urls(view, custom_patterns=None):
    """
    Generate CRUD URL patterns for a given view and model.

    Args:
        view (BaseView): The view class to use for the CRUD operations.
        custom_patterns (dict): Optional custom URL patterns and names.

    Returns:
        list: A list of URL patterns.
    
    Raises:
        ValueError: If the model attribute is not provided in the view.
    """
    # Ensure the view has a model attribute
    if not hasattr(view, 'model') or view.model is None:
        raise ValueError("The model attribute is empty, please provide a valid model")

    # Get the model name from the view
    model_name = view.model._meta.model_name
    
    # Prepare the view instance to avoid multiple calls to view.as_view()
    view_instance = view.as_view()

    # Default URL patterns for CRUD operations
    default_patterns = {
        'list': ('', view_instance, f'{model_name}_list'),          # URL pattern for listing objects
        'add': ('create/', view_instance, f'{model_name}_create'),  # URL pattern for creating a new object
        'detail': ('<int:pk>/', view_instance, f'{model_name}_detail'),  # URL pattern for viewing object details
        'update': ('<int:pk>/update/', view_instance, f'{model_name}_update'),  # URL pattern for updating an object
        'delete': ('<int:pk>/delete/', view_instance, f'{model_name}_delete'),  # URL pattern for deleting an object
    }

    # Override default patterns with custom patterns if provided
    if custom_patterns:
        default_patterns.update(custom_patterns)

    # Generate URL patterns by iterating over the default (or custom) patterns
    urlpatterns = [
        path(pattern, view_instance, name=name)  # Create a path for each pattern
        for pattern, view_instance, name in default_patterns.values()
    ]

    return urlpatterns  # Return the list of URL patterns
