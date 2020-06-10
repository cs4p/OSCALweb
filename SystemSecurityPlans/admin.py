from django.contrib import admin
from django.apps import apps
from SystemSecurityPlans import models

# Register your models here.

def changeRoll(old_role,new_role):
    controls = models.implementedRequirements.objects.filter(responsibleRoles=models.roles.objects.filter(title=old_role)[0].pk)
    for item in controls:
        item.responsibleRoles.add(models.roles.objects.filter(title=new_role)[0].pk)
        item.responsibleRoles.remove(models.roles.objects.filter(title=old_role)[0].pk)
    models.roles.objects.filter(title=old_role)[0].delete()

def delUnusedRoles():
    r = models.roles.objects.all()
    for item in r:
        if item.implementedrequirements_set.count() == 0:
            print('deleting ' + item.title)
            item.delete()

@admin.register(models.systemSecurityPlan)
class systemSecurityPlanAdmin(admin.ModelAdmin):
    filter_horizontal = ['documentID','properties','links','sspRoles','locations','parties','responsibleParty','systemComponents','controlImplementations','backMatter']

    def __str__(self):
        return "System Security Plans (SSPs)"

@admin.register(models.implementedRequirements)
class implementedRequirementsAdmin(admin.ModelAdmin):
    filter_horizontal = ['responsibleRoles','parameters','properties','statements','annotations','links']
    list_filter = ['responsibleRoles']

@admin.register(models.properties)
class propertiesAdmin(admin.ModelAdmin):
    pass



# Addr lines
# Addresss
# Annotationss
# Attachmentss
# Authorized privilegess
# Citationss
# Email addressess
# Hashess
# Implemented requirementss
# Information type impactss
# Information typess
# Inventory componentss
# Inventory itemss
# Linkss
# Locationss
# Orgss
# Partiess
# Personss
# Port rangess
# Propertiess
# Resourcess
# Rlinkss
# Roless
# Ssp interconnections
# Ssp protocolss
# Statementss
# Statuss
# System characteristicss
# System componentss
# System functionss
# System implementations
# System information typess
# System inventorys
# System parameterss
#
# System servicess
# Telephone numberss
# Ur lss
# Userss


# all other models
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass