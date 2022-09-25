from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import UserProjectAssignment, TeamMember, Project

class PeopleAdmin(ImportExportModelAdmin):
    list_display = ('name','email')

class AssignmentAdmin(ImportExportModelAdmin):
    list_display = ('userName','project')

    def userName(self,assigment):
        return '{} {}'.format(assigment.user.first_name,assigment.user.last_name)

class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('name', 'assigneesNames', 'projectIdentifier')

    def assigneesNames(self,project):
        assignees = ""
        for asignee in project.assignees.all():
            assignees += asignee.name+', '

        return assignees[:-2]

admin.site.register(Project,ProjectAdmin)
admin.site.register(UserProjectAssignment,AssignmentAdmin)
admin.site.register(TeamMember,PeopleAdmin)
