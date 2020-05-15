from django.db import models

# Define some common field types

class customMany2ManyField(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


class customTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2000
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        del kwargs['blank']
        return name, path, args, kwargs

class status(models.Model):
    state = models.CharField(max_length=30)
    description = models.CharField(max_length=80)
    remarks = customTextField()

    def __str__(self):
        return self.state


class properties(models.Model):
    value = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    propertyID = models.CharField(max_length=25, blank=True)
    ns = models.CharField(max_length=25, blank=True)
    prop_class = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name


class links(models.Model):
    text = models.CharField(max_length=100)
    href = models.CharField(max_length=100)
    rel = models.CharField(max_length=100, blank=True)
    mediaType = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.text


class documents(models.Model):
    identifier = models.CharField(max_length=25)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.identifier


class annotations(models.Model):
    name = models.CharField(max_length=100)
    annotationID = models.CharField(max_length=25)
    ns = models.CharField(max_length=100)
    value = customTextField()
    remarks = customTextField()

    def __str__(self):
        return self.name


class systemFunctions(models.Model):
    title = models.CharField(max_length=100)
    description = customTextField()

    def __str__(self):
        return self.title


class authorizedPrivileges(models.Model):
    title = models.CharField(max_length=100)
    description = customTextField()
    functionsPerformed = customMany2ManyField(systemFunctions)

    def __str__(self):
        return self.title


class roles(models.Model):
    title = models.CharField(max_length=100)
    shortName = models.CharField(max_length=25)
    desc = models.CharField(max_length=100)
    authorizedPrivileges = customMany2ManyField(authorizedPrivileges)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField()

    def __str__(self):
        return self.title


class addrLine(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value


class address(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    postalAddress = customMany2ManyField(addrLine)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    postalCode = models.CharField(max_length=25)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class emailAddresses(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


class telephoneNumbers(models.Model):
    number = models.CharField(max_length=25)
    type = models.CharField(max_length=25)

    def __str__(self):
        r = self.type + ': ' + self.number
        return r


class URLs(models.Model):
    uri = models.CharField(max_length=100)

    def __str__(self):
        return self.uri


class locations(models.Model):
    locationID = models.CharField(verbose_name='location description', max_length=25)
    addresses = models.ForeignKey(address, on_delete=models.PROTECT)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField()

    def __str__(self):
        return self.locationID


class orgs(models.Model):
    orgName = models.CharField(max_length=100)
    shortName = models.CharField(max_length=25)
    addresses = customMany2ManyField(address)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField()

    def __str__(self):
        return self.orgName


class persons(models.Model):
    personName = models.CharField(max_length=100)
    shortName = models.CharField(max_length=25)
    orgs = customMany2ManyField(orgs)
    addresses = customMany2ManyField(address)
    emailAddresses = customMany2ManyField(emailAddresses)
    telephoneNumbers = customMany2ManyField(telephoneNumbers)
    URLs = customMany2ManyField(URLs)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField()

    def __str__(self):
        return self.personName


class parties(models.Model):
    partyID = models.CharField(verbose_name='Party Description', max_length=100)
    persons = customMany2ManyField(persons)
    orgs = customMany2ManyField(orgs)

    def __str__(self):
        return self.partyID


class informationTypeImpacts(models.Model):
    impactType = models.CharField(max_length=25)  # Confidentiality, Integrity or availability
    properties = customMany2ManyField(properties)
    base = models.CharField(max_length=25)  # High, Medium, or Low
    selected = models.CharField(max_length=25)  # High, Medium, or Low
    adjustmentJustification = customTextField()

    def __str__(self):
        return self.impactType


class informationTypes(models.Model):
    InfoTypeID = models.CharField(max_length=25)
    title = models.CharField(max_length=100)
    description = customTextField()
    properties = customMany2ManyField(properties)
    confidentialityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)
    integrityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)
    availabilityImpact = models.ForeignKey(informationTypeImpacts, related_name='+', on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class systemInformationTypes(models.Model):
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    informationTypes = models.ForeignKey(informationTypes, on_delete=models.PROTECT)

    def __str__(self):
        return self.informationTypes


class attachments(models.Model):
    value = models.BinaryField()
    filename = models.CharField(max_length=100)
    mediaType = models.CharField(max_length=100)

    def __str__(self):
        return self.filename


class images(models.Model):
    description = customTextField()
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    image = models.ForeignKey(attachments, on_delete=models.PROTECT)
    caption = models.CharField(max_length=200)
    remarks = customTextField()

    def __str__(self):
        return self.image.filename


class diagrams(models.Model):
    type = models.CharField(max_length=100)  # authorizationBoundary, networkArchitecture, dataFlow
    description = customTextField()
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    remarks = customTextField()
    diagrams = customMany2ManyField(images)

    def __str__(self):
        return self.type


class systemCharacteristics(models.Model):
    systemName = models.CharField(max_length=100)
    systemNameShort = models.CharField(max_length=25)
    description = customTextField()
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    dateAuthorized = models.DateTimeField()
    securitySensitivityLevel = models.CharField(max_length=25)
    status = customMany2ManyField(status)
    remarks = customTextField()
    leveragedAuthorizations = models.CharField(max_length=200, blank=True)
    authorizationBoundary = customMany2ManyField(diagrams, related_name='+')
    networkArchitecture = customMany2ManyField(diagrams, related_name='+')
    dataFlow = customMany2ManyField(diagrams, related_name='+')

    def __str__(self):
        return self.systemName


class users(models.Model):
    title = models.CharField(max_length=100)
    shortName = models.CharField(max_length=25)
    description = models.CharField(max_length=100)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    roles = customMany2ManyField(roles)

    def __str__(self):
        return self.title


class systemImplementation(models.Model):
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    user = customMany2ManyField(users)
    remarks = customTextField()


class systemComponents(models.Model):
    componentType = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    status = customMany2ManyField(status)
    responsibleRoles = customMany2ManyField(roles)
    remarks = customTextField()

    def __str__(self):
        return self.title


class portRanges(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    transport = models.CharField(max_length=40)

    def __str__(self):
        r = str(self.start) + '-' + str(self.end) + ' ' + self.transport
        return r


class sspProtocols(models.Model):
    protocalID = models.CharField(max_length=25)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    portRanges = customMany2ManyField(portRanges)

    def __str__(self):
        return self.name


class systemServices(models.Model):
    serviceID = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    sspProtocol = customMany2ManyField(sspProtocols)
    purpose = customTextField()
    remarks = customTextField()

    def __str__(self):
        return self.title


class sspInterconnection(models.Model):
    InterconnectID = models.CharField(max_length=25)
    remoteSystemName = models.CharField(max_length=100)
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    remarks = customTextField()

    def __str__(self):
        return self.remoteSystemName


class inventoryComponents(models.Model):
    use = customTextField()
    systemComponent = customMany2ManyField(systemComponents)
    remarks = customTextField()


class inventoryItems(models.Model):
    itemID = models.CharField(max_length=100)
    assetID = models.CharField(max_length=100)
    description = customTextField()
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    inventoryComponents = customMany2ManyField(inventoryComponents)
    remarks = customTextField()

    def __str__(self):
        return self.itemID


class systemInventory(models.Model):
    inventoryItems = customMany2ManyField(inventoryItems)
    remarks = customTextField()


class systemParameters(models.Model):
    paramID = models.CharField(max_length=25)
    value = customTextField()

    def __str__(self):
        return self.paramID


class implementationComponents(models.Model):
    systemComponent = customMany2ManyField(systemComponents)
    systemParameters = customMany2ManyField(systemParameters)


class statements(models.Model):
    statementID = models.CharField(max_length=25)
    description = customTextField()
    properties = customMany2ManyField(properties)
    links = customMany2ManyField(links)
    responsibleRoles = customMany2ManyField(roles)
    implementationComponents = customMany2ManyField(implementationComponents)
    remarks = customTextField()

    def __str__(self):
        return self.statementID


class implementedRequirements(models.Model):
    requirementID = models.CharField(max_length=25)
    controlID = models.CharField(max_length=25)
    description = customTextField()
    properties = customMany2ManyField(properties)
    annotations = customMany2ManyField(annotations)
    links = customMany2ManyField(links)
    implementationComponents = customMany2ManyField(implementationComponents)
    responsibleRoles = customMany2ManyField(roles)
    systemParameters = customMany2ManyField(systemParameters)
    statements = customMany2ManyField(statements)
    remarks = customTextField()

    def __str__(self):
        return self.controlID + ' - ' + self.requirementID


class citations(models.Model):
    text = customTextField()
    properties = customMany2ManyField(properties)
    biblio = customTextField()

    def __str__(self):
        return self.text


class hashes(models.Model):
    value = customTextField()
    algorithm = models.CharField(max_length=100)

    def __str__(self):
        return self.algorithm


class rlinks(models.Model):
    link = models.ForeignKey(links, on_delete=models.PROTECT)
    hash = models.ForeignKey(hashes, on_delete=models.PROTECT)

    def __str__(self):
        return self.link


class resources(models.Model):
    resourceID = models.CharField(max_length=25)
    title = models.CharField(max_length=100)
    description = customTextField()
    properties = customMany2ManyField(properties)
    documents = customMany2ManyField(documents)
    citations = customMany2ManyField(citations)
    rlinks = customMany2ManyField(rlinks)
    attachments = customMany2ManyField(attachments)
    remarks = customTextField()

    def __str__(self):
        return self.title


class systemSecurityPlan(models.Model):
    sspID = models.CharField(max_length=25)
    title = models.CharField(max_length=100)
    published = models.DateTimeField()
    lastModified = models.DateTimeField()
    version = models.CharField(max_length=25)
    oscalVersion = models.CharField(max_length=10, default='1.0.0')
    # revisionHistory = models.ForeignKey(systemSecurityPlanHistory, on_delete=models.PROTECT)
    documentID = customMany2ManyField(documents, blank=True)
    properties = customMany2ManyField(properties)
    links = customMany2ManyField(links)
    sspRoles = customMany2ManyField(roles)
    locations = customMany2ManyField(locations)
    parties = customMany2ManyField(parties)
    responsibleParty = customMany2ManyField(roles, related_name='+')
    remarks = customTextField()
    systemCharacteristics = models.ForeignKey(systemCharacteristics, on_delete=models.PROTECT, null=True)
    # systemImplementations = models.ForeignKey(systemImplementation, on_delete=models.PROTECT, null=True)
    systemComponents = customMany2ManyField(systemComponents)
    controlImplementations = customMany2ManyField(implementedRequirements)
    backMatter = customMany2ManyField(resources)

    def __str__(self):
        return self.title
