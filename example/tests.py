from django.urls import reverse
from django.test import TestCase, RequestFactory, Client

from example.models import Employee
from example.views import EmployeeView
from example.forms import EmployeeForm



class EmployeeViewTests(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.employee = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            bio='A test employee'
        )

    def test_get_model(self):
        view = EmployeeView()
        self.assertEqual(view.get_model(), Employee)

    def test_get_single_object_name(self):
        view = EmployeeView()
        self.assertEqual(view.get_single_object_name(), 'employee')

    def test_get_plural_object_name(self):
        view = EmployeeView()
        self.assertEqual(view.get_plural_object_name(), 'employees')

    def test_list_view(self):
        request = self.factory.get(reverse('example:employee_list'))
        response = EmployeeView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        request = self.factory.get(reverse('example:employee_detail', kwargs={'pk': self.employee.pk}))
        response = EmployeeView.as_view()(request, pk=self.employee.pk)
        self.assertEqual(response.status_code, 200)

    def test_create_view_get(self):
        request = self.factory.get(reverse('example:employee_create'))
        response = EmployeeView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_create_view_post(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'bio': 'Another test employee'
        }
        request = self.factory.post(reverse('example:employee_create'), data)
        response = EmployeeView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        self.assertEqual(Employee.objects.count(), 2)

    def test_update_view_get(self):
        request = self.factory.get(reverse('example:employee_update', kwargs={'pk': self.employee.pk}))
        response = EmployeeView.as_view()(request, pk=self.employee.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_update_view_post(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'bio': 'Updated test employee'
        }
        request = self.factory.post(reverse('example:employee_update', kwargs={'pk': self.employee.pk}), data)
        response = EmployeeView.as_view()(request, pk=self.employee.pk)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.last_name, 'Smith')

    def test_delete_view(self):
        request = self.factory.post(reverse('example:employee_delete', kwargs={'pk': self.employee.pk}))
        response = EmployeeView.as_view()(request, pk=self.employee.pk)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful deletion
        self.assertEqual(Employee.objects.count(), 0)

    def test_get_template_name(self):
        view = EmployeeView()
        self.assertEqual(view.get_template_name('list'), 'employee/employee_list.html')

    def test_get_redirect_url(self):
        view = EmployeeView()
        self.assertEqual(view.get_redirect_url(), 'example:employee_list')

    def test_get_queryset(self):
        view = EmployeeView()
        self.assertEqual(list(view.get_queryset(None)), [self.employee])

    def test_get_object(self):
        view = EmployeeView()
        view.kwargs = {'pk': self.employee.pk}
        self.assertEqual(view.get_object(None), self.employee)

    def test_get_form_class(self):
        view = EmployeeView()
        self.assertEqual(view.get_form_class(), EmployeeForm)


class TestRightViewMethodRouting(TestCase):
    
    def setUp(self) -> None:
        self.client = Client()
    
    def test_list_employees(self):
        response = self.client.get("/employees/")
        content: bytes = response.content
        start_title_index = content.find(b"title")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["employees"]), 0)
        self.assertEqual(content[start_title_index+6:start_title_index+6+13], b'Employee List')
    
    def test_get_employee(self):
        employee = Employee.objects.create(first_name='John', last_name='Doe', bio='A test employee')

        response = self.client.get(f"/employees/{employee.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["employee"], employee)
    
    def test_update_employee(self):
        employee = Employee.objects.create(first_name='John', last_name='Doe', bio='A test employee')

        response = self.client.post(f"/employees/{employee.id}/update/", data={"first_name": "Maamoun"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["employee"].first_name, "Maamoun")

    def test_delete_employee(self):
        employee = Employee.objects.create(first_name='John', last_name='Doe', bio='A test employee')

        response1 = self.client.post(f"/employees/{employee.id}/delete/")
        # note: after delete -> redirect to list_view
        self.assertEqual(response1.status_code, 302)

        redirected_url = response1.headers["Location"]
        response2 = self.client.get(redirected_url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.context["employees"]), 0)

    def test_create_employee(self):
        data = dict(first_name="John", last_name='Doe', bio='A test employee')

        response1 = self.client.post(f"/employees/create/", data=data)
        # note: after create -> redirect to list_view
        self.assertEqual(response1.status_code, 302)

        redirected_url = response1.headers["Location"]
        response2 = self.client.get(redirected_url)
        self.assertEqual(response2.context["employees"].first().last_name, "Doe")
