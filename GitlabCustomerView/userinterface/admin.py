from django.contrib import admin

from .models import Customer, Employee, Project

class PeopleAdmin(admin.ModelAdmin):
    list_display = ('name','email')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','customerName', 'assigneesNames', 'gitlabProjectId')

    def customerName(self,project):
        return project.customer.name

    def assigneesNames(self,project):
        assignees = ""
        for asignee in project.assignees.all():
            assignees += asignee.name+', '

        return assignees[:-2]

admin.site.register(Project,ProjectAdmin)
admin.site.register(Customer,PeopleAdmin)
admin.site.register(Employee,PeopleAdmin)
