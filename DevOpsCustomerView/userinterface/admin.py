from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Company, CustomerUser, DownloadableFile, Project, Team, TeamMember, UserProjectAssignment

class PeopleAdmin(ImportExportModelAdmin):
    list_display = ('get_name', 'get_email', 'role')

    def get_name(self, obj: TeamMember) -> str:
        return obj.user.username
    get_name.admin_order_field = 'user__username'
    get_name.short_description = 'Name'

    def get_email(self, obj: TeamMember) -> str:
        return obj.user.email
    get_email.admin_order_field = 'user__email'
    get_email.short_description = 'Email'

class AssignmentAdmin(ImportExportModelAdmin):
    list_display = ('get_team_names', 'project')

    def get_team_names(self, assignment: UserProjectAssignment) -> str:
        team_names = [team.name for team in assignment.teams.all()]
        return ', '.join(team_names) if team_names else 'No Teams Assigned'
    get_team_names.short_description = 'Team Names'

class ProjectAdmin(ImportExportModelAdmin):
    list_display = ('name', 'first_email_address', 'get_assignees_names', 'project_identifier')
    exclude = ('private_url_hash',)

    def get_assignees_names(self, project: Project) -> str:
        return ', '.join([assignee.user.username for assignee in project.assignees.all()])
    get_assignees_names.short_description = 'Assignees'

class DownloadableFileAdmin(ImportExportModelAdmin):
    list_display = ('name', 'project')

class CompanyAdmin(ImportExportModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone')

class CustomerUserAdmin(ImportExportModelAdmin):
    list_display = ('get_username', 'company', 'enable_notifications', 'can_handle_contracts')

    def get_username(self, obj: CustomerUser) -> str:
        return obj.user.username
    get_username.admin_order_field = 'user__username'
    get_username.short_description = 'Username'

class TeamAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description')

admin.site.register(Company, CompanyAdmin)
admin.site.register(CustomerUser, CustomerUserAdmin)
admin.site.register(DownloadableFile, DownloadableFileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, PeopleAdmin)
admin.site.register(UserProjectAssignment, AssignmentAdmin)