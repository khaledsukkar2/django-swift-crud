# Create your views here.
from swift_crud.views import SwiftView
from .models import Employee
from .forms import EmployeeForm

class EmployeeView(SwiftView):
    model = Employee
    form_class = EmployeeForm
    verbose_name = 'employee'
    verbose_name_plural = 'employees'
    template_folder = 'employee'
    redirect_url = 'example:employee_list'
