# Create your views here.
from simple_crud.views import BaseView
from .models import Employee
from .forms import EmployeeForm

class EmployeeView(BaseView):
    model = Employee
    form_class = EmployeeForm
    single_object_name = 'employee'
    plural_object_name = 'employees'
    template_folder = 'employee'
    redirect_url = 'example:employee_list'
