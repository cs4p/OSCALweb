from django.contrib import admin
from django.apps import apps
from SystemSecurityPlans import models

# Register your models here.

def changeRoll(old_role,new_role):
    controls = models.system_control.objects.filter(responsibleRoles=models.user_role.objects.filter(title=old_role)[0].pk)
    for item in controls:
        item.responsibleRoles.add(models.user_role.objects.filter(title=new_role)[0].pk)
        item.responsibleRoles.remove(models.user_role.objects.filter(title=old_role)[0].pk)
    models.user_role.objects.filter(title=old_role)[0].delete()

def delUnusedRoles():
    r = models.user_role.objects.all()
    for item in r:
        if item.system_control_set.count() == 0:
            print('deleting ' + item.title)
            item.delete()


def listRolesWithControlCount():
    r = models.user_role.objects.all()
    role_dictionary = {}
    for role in r:
        role_dictionary[role.title] = role.control_statement_set.count()
    sort_roles = sorted(role_dictionary.items(), key=lambda x: x[1], reverse=True)

    for i in sort_roles:
        print(i[0], i[1])



@admin.register(models.system_security_plan)
class systemSecurityPlanAdmin(admin.ModelAdmin):
    #filter_horizontal = ['documentID','properties','links','sspRoles','locations','parties','responsibleParty','systemComponents','controlImplementations','backMatter']

    def __str__(self):
        return "System Security Plans (SSPs)"

@admin.register(models.system_control)
class system_controlAdmin(admin.ModelAdmin):
    #filter_horizontal = ['responsibleRoles','parameters','properties','statements','annotations','links']
    list_filter = ['control_responsible_roles']

@admin.register(models.property)
class propertyAdmin(admin.ModelAdmin):
    pass



# all other models
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass