from django.db import models
from django.utils.timezone import now

# Define some common field types


class customMany2ManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


class customTextField(models.CharField):
    def __init__(self,len, *args, **kwargs):
        if len == 'short':
            kwargs['max_length'] = 25
        elif len == 'medium':
            kwargs['max_length'] = 100
        elif len == 'long':
            kwargs['max_length'] = 1000
            kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["len"] = len
        return name, path, args, kwargs

class shortText(models.CharField):
    description = "A short (25 characters) text field that does not allow blanks"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 25
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs


class mediumText(models.CharField):
    description = "A 100 character text field that does not allow blanks"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs


class longText(models.CharField):
    description = "A 1000 character text field that does allow blanks"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        del kwargs['blank']
        return name, path, args, kwargs

class properties(models.Model):
    value = customTextField(len='medium')
    name = customTextField(len='medium')
    propertyID = customTextField(len='short')
    ns = customTextField(len='medium')
    prop_class = customTextField(len='medium')


class links(models.Model):
    text = customTextField(len='medium')
    href = customTextField(len='medium')
    rel = customTextField(len='medium')
    mediaType = customTextField(len='medium')


class documents(models.Model):
    identifier = customTextField(len='short')
    type = customTextField(len='medium')


class annotations(models.Model):
    name = customTextField(len='medium')
    annotationID = customTextField(len='short')
    ns = customTextField(len='medium')
    value = customTextField(len='long')
    remarks = customTextField(len='long')


class roles(models.Model):
    roleID = customTextField(len='short')
    title = customTextField(len='short')
    shortName = customTextField(len='short')
    desc = customTextField(len='short')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField(len='long')


class addrLine(models.Model):
    value = customTextField(len='medium')


class address(models.Model):
    type = customTextField(len='medium')
    postalAddress = customMany2ManyField(addrLine)
    city = customTextField(len='medium')
    state = models.CharField(max_length=2)
    postalCode = customTextField(len='short')
    country = customTextField(len='medium')


class emailAddresses(models.Model):
    email = models.CharField(max_length=50)


class telephoneNumbers(models.Model):
    number = customTextField(len='short')
    type = customTextField(len='short')


class URLs(models.Model):
    uri = customTextField(len='medium')


class locations(models.Model):
    locationID = customTextField(len='short')
    addresses = models.ForeignKey(address, on_delete=models.PROTECT)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField(len='long')


class orgs(models.Model):
    orgName = customTextField(len='medium')
    shortName = models.CharField(max_length=15)
    addresses = customMany2ManyField(address)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField(len='long')


class persons(models.Model):
    personName = customTextField(len='medium')
    shortName = models.CharField(max_length=15)
    orgs = customMany2ManyField(orgs)
    addresses = customMany2ManyField(address)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField(len='long')


class parties(models.Model):
    partyID = customTextField(len='short')
    persons = customMany2ManyField(persons)


class informationTypeImpacts(models.Model):
    impactType = models.CharField(max_length=15)  # Confidentiality, Integrity or availability
    properties = customMany2ManyField(properties)
    base = models.CharField(max_length=15)  # High, Medium, or Low
    selected = models.CharField(max_length=15)  # High, Medium, or Low
    adjustmentJustification = customTextField(len='long')


class informationTypes(models.Model):
    InfoTypeID = customTextField(len='short')
    title = customTextField(len='medium')
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    confidentialityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)
    integrityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)
    availabilityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)


class systemInformationTypes(models.Model):
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    informationTypes = models.ForeignKey(informationTypes, on_delete=models.PROTECT)


class attachments(models.Model):
    value = models.BinaryField()
    filename = customTextField(len='medium')
    mediaType = customTextField(len='medium')


class images(models.Model):
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    image = models.ForeignKey(attachments, on_delete=models.PROTECT)
    caption = models.CharField(max_length=200)
    remarks = customTextField(len='long')


class diagrams(models.Model):
    type = customTextField(len='short')  # authorizationBoundary, networkArchitecture, dataFlow
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField(len='long')
    diagrams = customMany2ManyField(images)


class systemCharacteristics(models.Model):
    systemName = customTextField(len='medium')
    systemNameShort = customTextField(len='short')
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    dateAuthorized = models.DateTimeField()
    securitySensitivityLevel = customTextField(len='short')
    status = customTextField(len='short')
    remarks = customTextField(len='long')
    leveragedAuthorizations = models.CharField(max_length=200, blank=True)
    authorizationBoundary = customMany2ManyField(diagrams, related_name='+')
    networkArchitecture = customMany2ManyField(diagrams, related_name='+')
    dataFlow = customMany2ManyField(diagrams, related_name='+')


class systemFunctions(models.Model):
    title = customTextField(len='medium')
    description = customTextField(len='long')


class authorizedPrivileges(models.Model):
    title = customTextField(len='medium')
    description = customTextField(len='long')
    functionsPerformed = customMany2ManyField(systemFunctions)


class users(models.Model):
    title = customTextField(len='medium')
    shortName = customTextField(len='short')
    description = customTextField(len='medium')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    roleIDs = customMany2ManyField(roles)
    authorizedPrivileges = customMany2ManyField(authorizedPrivileges)


class systemImplementation(models.Model):
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    user = customMany2ManyField(users)
    remarks = customTextField(len='long')


class systemComponents(models.Model):
    componentType = customTextField(len='medium')
    title = customTextField(len='medium')
    description = customTextField(len='medium')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    status = customTextField(len='short')
    responsibleRoles = customMany2ManyField(roles)
    remarks = customTextField(len='long')


class portRanges(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    transport = models.CharField(max_length=40)


class sspProtocols(models.Model):
    protocalID = customTextField(len='short')
    name = customTextField(len='medium')
    title = customTextField(len='medium')
    portRanges = customMany2ManyField(portRanges)


class systemServices(models.Model):
    serviceID = customTextField(len='medium')
    title = customTextField(len='medium')
    description = customTextField(len='medium')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    sspProtocol = customMany2ManyField(sspProtocols)
    purpose = customTextField(len='long')
    remarks = customTextField(len='long')


class sspInterconnection(models.Model):
    InterconnectID = customTextField(len='short')
    remoteSystemName = customTextField(len='medium')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    remarks = customTextField(len='long')


class inventoryComponents(models.Model):
    use = customTextField(len='long')
    systemComponent = customMany2ManyField(systemComponents)
    remarks = customTextField(len='long')


class inventoryItems(models.Model):
    itemID = models.CharField(max_length=15)
    assetID = models.CharField(max_length=15)
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    inventoryComponents = customMany2ManyField(inventoryComponents)
    remarks = customTextField(len='long')


class systemInventory(models.Model):
    inventoryItems = customMany2ManyField(inventoryItems)
    remarks = customTextField(len='long')


class systemParameters(models.Model):
    paramID = customTextField(len='short')
    value = customTextField(len='long')


class implementationComponents(models.Model):
    systemComponent = customMany2ManyField(systemComponents)
    systemParameters = customMany2ManyField(systemParameters)


class statements(models.Model):
    statementID = models.CharField(max_length=15)
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    implementationComponents = customMany2ManyField(implementationComponents)
    remarks = customTextField(len='long')


class implementedRequirements(models.Model):
    requirementID = customTextField(len='short')
    controlID = customTextField(len='short')
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    implementationComponents = customMany2ManyField(implementationComponents)
    responsibleRoles = customMany2ManyField(roles)
    systemParameters = customMany2ManyField(systemParameters)
    statements = customMany2ManyField(statements)
    remarks = customTextField(len='long')


class controlImplementation(models.Model):
    description = customTextField(len='long')
    implementedRequirements = customMany2ManyField(implementedRequirements)


class citations(models.Model):
    text = customTextField(len='long')
    properties = customMany2ManyField(properties)
    biblio = customTextField(len='long')


class hashes(models.Model):
    value = customTextField(len='long')
    algorithm = customTextField(len='medium')


class rlinks(models.Model):
    link = models.ForeignKey(links, on_delete=models.PROTECT)
    hash = models.ForeignKey(hashes, on_delete=models.PROTECT)


class resources(models.Model):
    resourceID = customTextField(len='short')
    title = customTextField(len='medium')
    description = customTextField(len='long')
    properties = customMany2ManyField(properties)
    documents = customMany2ManyField(documents)
    citations = customMany2ManyField(citations)
    rlinks = customMany2ManyField(rlinks)
    attachments = customMany2ManyField(attachments)
    remarks = customTextField(len='long')


class backMatter(models.Model):
    resources = customMany2ManyField(resources)


# class systemSecurityPlanHistory(models.Model):
#     sspID = customTextField(len='short')
#     title = customTextField(len='medium')
#     published = models.DateTimeField()
#     lastModified = models.DateTimeField()
#     version = customTextField(len='short')
#     oscalVersion = customTextField(len='short')
#     properties = customMany2ManyField(properties)
#     documentID = customMany2ManyField(documents)
#     links = customMany2ManyField(links)
#     sspRoles = customMany2ManyField(roles)
#     locations = customMany2ManyField(locations)
#     parties = customMany2ManyField(parties)
#     responsibleParty = customMany2ManyField(roles, related_name='+')
#     remarks = customTextField(len='long')
#     systemCharacteristics = models.ForeignKey(systemCharacteristics, on_delete=models.PROTECT)
#     systemImplementation = models.ForeignKey(systemImplementation, on_delete=models.PROTECT)
#     controlImplementation = models.ForeignKey(controlImplementation, on_delete=models.PROTECT)
#     backMatter = models.ForeignKey(backMatter, on_delete=models.PROTECT)


class systemSecurityPlan(models.Model):
    sspID = customTextField(len='short')
    title = customTextField(len='medium')
    published = models.DateTimeField(default=now())
    lastModified = models.DateTimeField(default=now())
    version = customTextField(len='short')
    oscalVersion = models.CharField(max_length=10, default='1.0.0')
    # revisionHistory = models.ForeignKey(systemSecurityPlanHistory, on_delete=models.PROTECT)
    documentID = customMany2ManyField(documents, blank=True)
    properties = customMany2ManyField(properties)
    links = customMany2ManyField(links)
    sspRoles = customMany2ManyField(roles)
    locations = customMany2ManyField(locations)
    parties = customMany2ManyField(parties)
    responsibleParty = customMany2ManyField(roles, related_name='+')
    remarks = customTextField(len='long')
    systemCharacteristics = models.ForeignKey(systemCharacteristics, on_delete=models.PROTECT, null=True)
    systemImplementation = models.ForeignKey(systemImplementation, on_delete=models.PROTECT, null=True)
    controlImplementation = models.ForeignKey(controlImplementation, on_delete=models.PROTECT, null=True)
    backMatter = models.ForeignKey(backMatter, on_delete=models.PROTECT, null=True)
