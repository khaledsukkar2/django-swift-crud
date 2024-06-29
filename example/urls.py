from swift_crud.utils import generate_crud_urls
from django.urls import path
from .views import EmployeeView
app_name = "example"
urlpatterns = [
    # path('', EmployeeView.as_view(), name="employee_list"),
    # path('create/', EmployeeView.as_view(), name="employee_create"),
    # path('update/<int:pk>/', EmployeeView.as_view(), name="employee_update"),
    # path('<int:pk>/', EmployeeView.as_view(), name="employee_detail"),
    # path('delete/<int:pk>/', EmployeeView.as_view(), name="employee_delete")
]

urlpatterns.extend(generate_crud_urls(EmployeeView))
