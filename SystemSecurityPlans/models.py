import uuid as uuid
from django.db import models
from tinymce.models import HTMLField

attachment_types = [('image', 'Image'),
                    ('diagram', 'Diagram'),
                    ('document', 'Document'),
                    ('other', 'Other File Type')]


# Define some common field types

# noinspection PyPep8Naming
class customMany2ManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


class customTextField(HTMLField):
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['blank']
        return name, path, args, kwargs


class namespaceField(models.CharField):
    def __init__(self, *args, **kwargs):
        verbose_name = 'name space'
        kwargs['blank'] = True
        kwargs['max_length'] = 25
        kwargs['help_text'] = "A namespace qualifying the name."
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['blank']
        del kwargs['max_length']
        del kwargs['help_text']
        return name, path, args, kwargs


class BaseFields(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=100, blank=True, help_text='A title for display and navigation')
    short_name = models.CharField(max_length=25, blank=True, help_text='A common name, short name or acronym')
    desc = customTextField('description', help_text='A short textual description')

    class Meta:
        abstract = True
        ordering = ["title"]

    def __str__(self):
        return self.title + '(' + self.short_name + ')'


# True lookup tables for storing select values
class status(BaseFields):
    """
    system implementation status. Normally:
    operational,
    under-development,
    under-major-modification,
    disposition, and
    other
    """

    class Meta:
        verbose_name_plural = "statuses"


impact_choices = [(1, "High"), (2, "Moderate"), (3, "Low")]


class information_type(BaseFields):
    """
    Management and support information and information systems impact levels
    as defined in NIST SP 800-60 APPENDIX C. Additional information types may be added
    by the user
    """
    confidentiality_impact = models.CharField(max_length=50, choices=impact_choices)
    integrity_impact = models.CharField(max_length=50, choices=impact_choices)
    availability_impact = models.CharField(max_length=50, choices=impact_choices)


class hashed_value(BaseFields):
    """
    used to store hashed values for validation of attachments or linked files
    """
    value = models.TextField()
    algorithm = models.CharField(max_length=100)


# These are common attributes of almost all objects


class prop(models.Model):
    class Meta:
        verbose_name = 'property'
        verbose_name_plural = 'properties'
        ordering = ['name']

    uuid = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4())
    name = models.CharField(max_length=100, help_text='The key for a key:value pair',blank=True)
    value = models.CharField(max_length=100, help_text='The value for a key:value pair')
    ns = namespaceField
    prop_class = models.CharField(max_length=25, blank=True,
                                  help_text="Indicating the type or classification of the containing object")


class link(models.Model):
    class Meta:
        # unique_together = [['href', 'text']]
        ordering = ['href', 'text']

    uuid = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4())
    text = models.CharField(max_length=100)
    href = models.CharField(max_length=100)
    requires_authentication = models.BooleanField(default=False)
    rel = models.CharField(max_length=100, blank=True,
                           help_text="Describes the type of relationship provided by the link. This can be an indicator of the link's purpose.")
    mediaType = models.CharField(max_length=100, blank=True)
    hash = models.ForeignKey(hashed_value, on_delete=models.CASCADE, blank=True, null=True)


class annotation(BaseFields):
    ns = namespaceField
    value = customTextField()
    remarks = customTextField()


class CommonInfo(BaseFields):
    """
    Add Property, Links, Annotations and Remarks to a table by inheriting this base class
    """
    properties = customMany2ManyField(prop)
    annotations = customMany2ManyField(annotation)
    links = customMany2ManyField(link)
    remarks = customTextField()

    class Meta:
        abstract = True


# Other common objects used in many places
class attachment(CommonInfo):
    class Meta:
        unique_together = [['attachment', 'title', 'caption']]

    attachment_type = models.CharField(max_length=50, choices=attachment_types)
    attachment = models.FileField()
    filename = models.CharField(max_length=100, blank=True)
    mediaType = models.CharField(max_length=100, blank=True)
    hash = models.ForeignKey(hashed_value, on_delete=models.CASCADE, null=True)
    caption = models.CharField(max_length=200, blank=True)


# elements of a user, role, and group
class user_function(BaseFields):
    """
    list of functions assigned to roles. e.g. backup servers, deploy software, etc.
    """
    privileged = models.BooleanField('Is this a privileged function?')


class user_privilege(BaseFields):
    functionsPerformed = customMany2ManyField(user_function)


class user_role(CommonInfo):
    user_privileges = customMany2ManyField(user_privilege)


# elements that can apply to a user, organization or both
class address(BaseFields):
    class Meta:
        ordering = ['title', 'country', 'state', 'city', 'postal_code']

    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    postal_address = customTextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=25)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.title


contactInfoType = [('work', 'Work'),
                   ('personal', 'Personal'),
                   ('shared', 'Shared'),
                   ('service', 'Service'),
                   ('other', 'Other')]


class email(models.Model):
    class Meta:
        ordering = ['email']

    email = models.EmailField()
    type = models.CharField(max_length=50, choices=contactInfoType, default='work')

    def __str__(self):
        return self.type + ': ' + self.email


class telephone_number(models.Model):
    class Meta:
        ordering = ['number']

    number = models.CharField(max_length=25)
    type = models.CharField(max_length=50, choices=contactInfoType, default='work')

    def __str__(self):
        return self.type + ': ' + self.number


class location(CommonInfo):
    address = models.ForeignKey(address, on_delete=models.CASCADE)
    emailAddresses = customMany2ManyField(email)
    telephoneNumbers = customMany2ManyField(telephone_number)


class organization(CommonInfo):
    """
    Groups of people
    """
    locations = customMany2ManyField(location)
    email_addresses = customMany2ManyField(email)
    telephone_numbers = customMany2ManyField(telephone_number)


class person(CommonInfo):
    """
    An individual who can be assigned roles within a system.
    """
    organizations = customMany2ManyField(organization)
    locations = customMany2ManyField(location)
    email_addresses = customMany2ManyField(email)
    telephone_numbers = customMany2ManyField(telephone_number)


class leveraged_authorization(models.Model):
    class Meta:
        ordering = ['leveraged_system_name']

    leveraged_system_name = models.CharField(max_length=255, unique=True)
    link_to_SSP = models.ForeignKey(link, on_delete=models.CASCADE)

    def __str__(self):
        return self.leveraged_system_name


# System Properties
class system_characteristic(CommonInfo):
    """
    required elements of a System Security Plan
    """
    system_status = models.ForeignKey(status, on_delete=models.CASCADE)
    leveraged_authorizations = customMany2ManyField(leveraged_authorization)
    authorization_boundary_diagram = models.ForeignKey(attachment, on_delete=models.CASCADE,
                                                       related_name='authorization_boundary_diagram', null=True)
    network_architecture_diagram = models.ForeignKey(attachment, on_delete=models.CASCADE,
                                                     related_name='network_architecture_diagram', null=True)
    data_flow_diagram = models.ForeignKey(attachment, on_delete=models.CASCADE, related_name='data_flow_diagram',
                                          null=True)


class system_information_type(models.Model):
    """
    If the cia impact of a particular information type is different for this system than the default, you can modify it here.
    To be honest, I'm not sure how this should work so it will probably need to change once we start using the tool
    """
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4())
    information_type = models.ForeignKey(information_type, on_delete=models.CASCADE,
                                         help_text='select the information type to override')
    system_information_type_name = models.CharField(max_length=255, blank=True,
                                                    help_text='If needed, you can over ride the default information type name')
    adjusted_confidentiality_impact = models.CharField(max_length=50,
                                                       choices=impact_choices, blank=True)
    adjusted_integrity_impact = models.CharField(max_length=50, choices=impact_choices,
                                                 blank=True)
    adjusted_availability_impact = models.CharField(max_length=50, choices=impact_choices,
                                                    blank=True)
    adjustment_justification = customTextField()

    def __str__(self):
        return self.system_information_type_name


class system_component(CommonInfo):
    """
    A component is a subset of the information system that is either severable or
    should be described in additional detail. For example, this might be an authentication
    provider or a backup tool.
    """
    component_type = models.CharField(max_length=100)
    component_information_types = customMany2ManyField(system_information_type,
                                                       help_text='select the types of information processed by this component')
    component_status = models.ForeignKey(status, on_delete=models.CASCADE, null=True)
    component_responsible_roles = customMany2ManyField(user_role)


class port_range(models.Model):
    """
    List just the unique port ranges. This cna be input to firewall rules.
    The range get's assigned to a protocol (and hence a purpose) in the protocal class
    """

    class Meta:
        ordering = ['start', 'end', 'transport']
        unique_together = [['start', 'end', 'transport']]

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4())
    start = models.IntegerField()
    end = models.IntegerField()
    transport = models.CharField(max_length=3, choices=[('tcp', 'tcp'), ('udp', 'udp'), ('any', 'any')])

    def __str__(self):
        return str(self.start) + '-' + str(self.end) + ' ' + self.transport


class protocol(BaseFields):
    portRanges = customMany2ManyField(port_range)


class system_service(CommonInfo):
    """
    A service is a capability offered by the information system. Exmaples of services include
    database access, apis, or authentication. Services are typically accessed by other systems or
    system components. System services should not to be confused with system functions which
    are typically accessed by users.
    """
    protocols = customMany2ManyField(protocol)
    service_purpose = customTextField()
    service_information_types = customMany2ManyField(system_information_type)


class system_interconnection(CommonInfo):
    remote_system_name = models.CharField(max_length=100)
    interconnection_responsible_roles = customMany2ManyField(user_role)


class inventory_item_type(CommonInfo):
    """
    generic role of an inventory item. For example, webserver, database server, network switch, edge router.
    All inventory items should be clasified into an inventory item type
    """
    inventory_item_type_name = models.CharField(max_length=100)
    use = customTextField()
    responsibleRoles = customMany2ManyField(user_role)
    baseline_configuration = models.ForeignKey(link, on_delete=models.CASCADE, blank=True,
                                               related_name='baseline_configuration')


class system_inventory_item(CommonInfo):
    """
    Physical (or virtual) items which make up the information system.
    """
    inventory_item_type = models.ForeignKey(inventory_item_type, on_delete=models.CASCADE)
    item_special_configuration_settings = customTextField()


# objects related to security controls

# Objects to hold control catalog data that should be displayed in the SSP

parameter_type_choices = [('label', 'Label'),
                          ('description', 'Description'),
                          ('constraint', 'Constraint'),
                          ('guidance', 'Guidance'),
                          ('value', 'Value'),
                          ('select', 'Select')]


class nist_control_parameter(models.Model):
    param_id = models.CharField(max_length=25)
    param_type = models.CharField(max_length=100, choices=parameter_type_choices)
    param_text = customTextField
    param_depends_on = models.CharField(max_length=100, blank=True)
    param_class = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.param_id


class nist_control(models.Model):
    group_id = models.CharField(max_length=2)
    group_title = models.CharField(max_length=50)
    control_id = models.CharField(max_length=7, unique=True)
    source = models.CharField(max_length=30)
    control_title = models.CharField(max_length=255)
    label = models.CharField(max_length=10)
    sort_id = models.CharField(max_length=10)
    status = models.CharField(max_length=30, blank=True)
    control_statement = customTextField
    nist_control_statement = customTextField
    nist_control_guidance = customTextField
    nist_control_objectives = customTextField
    nist_control_objects = customTextField
    parameters = customMany2ManyField(nist_control_parameter)
    links = customMany2ManyField(link)
    annotations = customMany2ManyField(annotation)

    def __str__(self):
        long_title = self.group_title + ' | ' + self.label + ' | ' + self.control_title
        return long_title

    def statement_view(self,part_name='Any'):
        parts = nist_control_part.objects.filter(control_id=self.id,part_name=part_name)
        ctrl_statement = '<div><p>'
        if part_name == 'statement' or part_name == 'Any':
            for obj in parts.filter(part_name='statement'):
                ctrl_statement = nist_control_part.objects.get(pk=obj.id).getPartText()
        if part_name == 'guidance' or part_name == 'Any':
            ctrl_statement += "<hr><b>Guidance:</b><br>"
            for obj in parts.filter(part_name='guidance'):
                ctrl_statement = nist_control_part.objects.get(pk=obj.id).getPartText()
        if part_name == 'objective' or part_name == 'Any':
            ctrl_statement += "<hr><b>Objective:</b><br>"
            for obj in parts.filter(part_name='objective'):
                control_objective = nist_control_part.objects.get(pk=obj.id).getPartText()
        if part_name == 'objects' or part_name == 'Any':
            ctrl_statement += "<hr><b>Objects:</b><br>"
            for obj in parts.filter(part_name='objects'):
                control_objects = nist_control_part.objects.get(pk=obj.id).getPartText()
        ctrl_statement += '</p></div>'
        return ctrl_statement


class nist_control_part(models.Model):
    control = models.ForeignKey(nist_control, on_delete=models.CASCADE)
    parent_part = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    part_id = models.CharField(max_length=25, blank=True)
    part_name = models.CharField(max_length=255)
    part_ns = models.CharField(max_length=255, blank=True)
    part_class = models.CharField(max_length=255, blank=True)
    part_title = models.CharField(max_length=255, blank=True)
    part_properties = customMany2ManyField(prop)
    prose = customTextField()
    links = customMany2ManyField(link)

    def __str__(self):
        long_title = str(self.control) + ' ('+ self.part_name +') | ' + self.getPartText(0,get_subparts=False)
        return long_title

    def getPartText(self,indent=0,get_subparts=True):
        partText = '&nbsp;' * indent
        part = nist_control_part.objects.get(pk=self.id)
        if self.part_properties:
            for p in self.part_properties.values():
                if p['name'] == 'label':
                    partText += p['value'] + ' '
                else:
                    partText += p['name'] + ': ' + p['value']
        if self.part_title:
            partText += "<b>" + self.part_title + "</b><br>"
        if self.prose:
            partText += str(self.prose) + "<br>"
        if get_subparts:
            subparts = nist_control_part.objects.filter(parent_part_id=self.id)
            if subparts:
                indent += 2
                for subpart in subparts:
                    partText += nist_control_part.objects.get(pk=subpart.id).getPartText(indent)
        return partText


class control_statement(CommonInfo):
    """
    responses to the requirements defined in each control.  control_statement_id should be
    in the format {control_id}_{requirement_id}.
    """
    control_statement_responsible_roles = customMany2ManyField(user_role)
    control_statement_text = customTextField()


class control_parameter(BaseFields):
    control_parameter_id = models.CharField(max_length=25)
    value = customTextField()

    def __str__(self):
        return self.control_parameter_id


control_implementation_status_choices = [
    ('Implemented', 'Implemented'),
    ('Partially implemented ', 'Partially implemented'),
    ('Planned ', 'Planned'),
    ('Alternative Implementation', 'Alternative Implementation'),
    ('Not applicable', 'Not applicable')]

control_origination_choices = [
    ('Service Provider Corporate ', 'Service Provider Corporate'),
    ('Service Provider System Specific ', 'Service Provider System Specific'),
    ('Service Provider Hybrid (Corporate and System Specific)', 'Service Provider Hybrid'),
    ('Configured by Customer (Customer System Specific) ', 'Configured by Customer'),
    ('Provided by Customer (Customer System Specific) ', 'Provided by Customer'),
    ('Shared (Service Provider and Customer Responsibility) ', 'Shared'),
    ('Inherited ', 'Inherited')]


class system_control(CommonInfo):

    control_responsible_roles = customMany2ManyField(user_role)
    control_parameters = customMany2ManyField(control_parameter)
    control_statements = customMany2ManyField(control_statement)
    control_status = models.CharField(max_length=100, choices=control_implementation_status_choices)
    control_origination = models.CharField(max_length=100, choices=control_origination_choices)
    nist_control = models.ForeignKey(nist_control, on_delete=models.CASCADE, null=True)

    def get_roles_list(self):
        # TODO: Figure out why this method always returns empty
        roleList = []
        for item in self.control_responsible_roles.values_list('title'):
            roleList.append(item[0])
        return roleList


class system_security_plan(CommonInfo):
    published = models.DateTimeField()
    lastModified = models.DateTimeField()
    version = models.CharField(max_length=25, default='1.0.0')
    oscalVersion = models.CharField(max_length=10, default='1.0.0')
    system_characteristics = models.ForeignKey(system_characteristic, on_delete=models.CASCADE)
    system_components = customMany2ManyField(system_component)
    system_services = customMany2ManyField(system_service)
    system_interconnections = customMany2ManyField(system_interconnection)
    system_inventory_items = customMany2ManyField(system_inventory_item)
    controls = customMany2ManyField(system_control)
