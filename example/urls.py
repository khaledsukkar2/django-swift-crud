from django.urls import path, include
from example.views import EmployeeView
from swift_crud.utils import generate_crud_urls


app_name = "example"

urlpatterns = [
    # path('', EmployeeView.as_view(), name="employee_list"),
    # path('create/', EmployeeView.as_view(), name="employee_create"),
    # path('update/<int:pk>/', EmployeeView.as_view(), name="employee_update"),
    # path('<int:pk>/', EmployeeView.as_view(), name="employee_detail"),
    # path('delete/<int:pk>/', EmployeeView.as_view(), name="employee_delete")
    path('', include(generate_crud_urls(EmployeeView)))
]

