# DJANGO-SWIFT-CRUD Package

## Motiviation

Creating CRUD operations for Django models can often be a tedious, especially when dealing with the complexities of Class-Based Views. With the swift_crud package, we provide a streamlined solution that eliminates the need to navigate through inheritance hierarchies and override methods. Our goal is to empower developers to quickly and efficiently set up CRUD operations for any Django model with just one view class, saving valuable time and ensuring a smoother development process. Let swift_crud simplify your workflow and enhance your productivity.

## Overview

The `swift_crud` package provides a base view class (`SwiftView`) and utility functions to quickly set up CRUD (Create, Read, Update, Delete) operations for any Django model with only one view class. This package aims to simplify the process by abstracting away the complexity of built-in Class-Based Views (CBVs) and the need to track the inheritance hierarchy to determine where to override methods.

The package includes several mixins to handle common tasks, such as:

- Rendering templates
- Managing redirects
- Handling querysets
- Processing forms

By utilizing these mixins, developers can easily implement CRUD functionality for their Django models without having to write boilerplate code or navigate the intricate details of the CBV.

## Installation

```
pip install django-swift-crud
```

## Usage

### Setting Up

1. **Create your Django model**:

   ```python
   from django.db import models

   class Employee(models.Model):
       first_name = models.CharField(max_length=150)
       last_name = models.CharField(max_length=150)
       bio = models.TextField()

       def __str__(self):
           return f"{self.first_name} {self.last_name}"
   ```

2. **Define your views**:

   ```python
   from swift_crud.views import SwiftView
   from .models import Employee
   from .forms import EmployeeForm  # You need to create this form

   class EmployeeView(SwiftView):
       model = Employee
       form_class = EmployeeForm
       verbose_name = 'employee'
       verbose_name_plural = 'employees'
       template_folder = 'employees'
       redirect_url = '/employees/'
       allowed_views = ["list", "detail", "delete", "create", "update"]
   ```

3. **URL Configuration**:

   The patterns in the (create, update, delete) URLs should contain the (create, update, 'delete) words, respectively (you can override this in the `get_view_method` or in the `dispatch` method):

   ```python
   from django.urls import path
   from .views import EmployeeView

   urlpatterns = [
       path('employees/', EmployeeView.as_view(), name='employee_list'),
       path('employees/create/', EmployeeView.as_view(), name='employee_create'),
       path('employees/<int:pk>/', EmployeeView.as_view(), name='employee_detail'),
       path('employees/<int:pk>/update/', EmployeeView.as_view(), name='employee_update'),
       path('employees/<int:pk>/delete/', EmployeeView.as_view(), name='employee_delete'),
   ]
   ```

   Alternatively, you can use the `DefaultRouter` class from the `swift_crud.routers` module inspired from DRF:

   ```python
   
   from example.views import EmployeeView
   from swift_crud.utils import generate_crud_urls
   from swift_crud.routers import DefaultRouter
   
   
   app_name = "example"
   
   router = DefaultRouter()
   router.register("Employee/", EmployeeView, "Employee")
   
   
   urlpatterns = [
   
   ]
   
   urlpatterns += router.urls
   ```

   And of course, you can customize the Router to fit your use case.

## Create Your Own `SwiftView`

You can customize the `SwiftView` class if you want to add more features or Mixin classes, such as the `LoginRequiredMixin`, and reuse your custom `SwiftView` class.

## Attributes

The `SwiftView` class supports the following attributes:

- `model`: The model associated with this view. If not provided, the `get_model` method will raise a `ValueError`.
- `verbose_name` (Optional): The context variable name for a single object. If not provided, it defaults to the model's verbose name.
- `verbose_name_plural` (Optional): The context variable name for a queryset of objects. If not provided, it defaults to the model's verbose name plural.
- `template_folder`: Path to the folder of your templates.
- `custom_templates` (Optional): A dictionary to provide custom template paths.
- `redirect_url`: The URL to redirect to.
- `queryset` (Optional): The queryset to use. If not provided, `self.model.objects.all()` will be the query.
- `pk_url_kwarg` (Optional): The URL keyword argument for the primary key.
- `paginate_by` (Optional): Number of items per page for pagination.
- `allowed_views` (Optional): The view methods you want the view to work with. The default is all existing methods.

## Contributing

If you find any bugs or have feature requests, please open an issue on GitHub. Contributions are welcome!

Now we are working on four main features that need some contribution:

- Support AJAX requests inside the package
- Urls cache mechanism to use when working with routers (only)
- Also, we need some help with regular expression for routers module (note: this is good resource to start from [Regular Expression with python tutorial](https://www.youtube.com/watch?v=AEE9ecgLgdQ&list=WL&index=157&pp=gAQBiAQB) )

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

This package was inspired by the need to quickly set up CRUD operations for Django models with minimal boilerplate code. Special thanks to the Django community for their continuous support and contributions.
