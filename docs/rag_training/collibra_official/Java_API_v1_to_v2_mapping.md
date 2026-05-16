# Java API v1 to v2 mapping

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/MigrationTo51/ref_java-api-v2-changes.htm

 

Java API v1 to v2 mapping

APIs

Workflows

Integrations

Pro tips

 

 

 

                Collibra sites
            

                Use this menu to easily navigate to Collibra sites, documentation, resource centers and community forums.
            

Collibra.com

 

Dashboard

 

Community

 

Developer Portal

 

Documentation

 

Marketplace

 

Product Resource Center

 

Support

 

University

 

 

APIs

Workflows

Integrations

Pro tips

 

 

Workflow Designer documentation
 

 
Workflows at Collibra

 

About the Workflow Designer
 

 
Enable the Workflow Designer

 
Workflow permissions

 

Creating workflows
 

 

Workflow basic configuration elements
 

 
Model keys

 
Workflow description

 
Process variables

 
Workflow dialog boxes

 
Create a pool and lanes

 
Create start and end events

 
Add workflow elements

 

Designing workflows
 

 
Workspaces

 
Models

 

Apps
 

 
Create a new app

 
Import apps

 
Move apps

 
App revisions

 
Add models to an app

 
App editor

 

Processes
 

 
Create a new process

 
Import processes

 
Process editor

 
Process editor menu bar

 
Canvas and configuration area

 

Process execution
 

 
The workflow user

 
Names and unique names in workflows

 
The "groovy-lib" folder

 
Upgrading your scripts for Collibra 2024.02 compatibility

 

Upgrading your scripts for Groovy 3 compatibility
 

 
Change Groovy switch statement

 
Adjusting for Groovy JavaBeans specification compatibility changes

 
Bulk operations in Groovy script tasks

 
Java API v1 to v2 mapping

 

Beans
 

 
API v2 in workflows

 
BusinessItem bean

 
Users bean

 
Event bean

 
Utility bean

 
Mail bean

 
Translation bean

 

Listeners
 

 
Alternatives to API v1 listeners

 
Overview of task listeners

 
Overview of execution listeners

 
Logging in workflows

 
Multi-instance variable aggregation

 

Shape repository
 

 
Start event

 
Timer start event

 
Signal start event

 
Error start event

 

User task
 

 
Candidate user expressions

 

Service task
 

 

Delegates
 

 
Alternatives to API v1 delegates

 
GetRelations and RemoveRelations delegates

 
AddRelation delegate

 
AddResourceRole and RemoveResourceRole delegates

 
GetTerm and RemoveTerm delegate

 
AddTerm delegate

 
GetAttribute and RemoveAttribute delegates

 
AddAttribute delegate

 
TermIntake delegate

 
ChangeStatus delegate

 
StartWorkflowInstance delegate

 
MailSender delegate

 
GetUserNames delegate

 
GetRelatedTerms delegate

 
CreateIssue delegate

 
ChangeIssueResponsibleCommunity delegate

 
AddComment delegate

 
Script task

 
Manual task

 
Email task

 
External API task

 
Collibra API task

 
Subprocess

 
Call activity

 
Event subprocess

 
Exclusive gateway

 
Parallel gateway

 
Inclusive gateway

 
Event-based gateway

 
Timer boundary event

 
Error boundary event

 
Signal boundary event

 
Message boundary event

 
Timer intermediate event

 
Signal catching intermediate event

 
Message catching intermediate event

 
Intermediate event

 
Signal throwing intermediate event

 
End event

 
Error end event

 
Terminate end event

 
Pool

 
Lane

 
Sequence flows

 
Text annotation

 

Forms
 

 
Create a new form

 
Import forms

 
Form editor

 
Form editor menu bar

 
Form canvas

 

Form components
 

 
Date

 
Multiline Text

 
Rich Text

 
Text

 
Tags

 
File Upload

 
Asset Type

 
Domain Type

 
Attribute Type

 
Relation Type

 
User

 
Group

 
Role

 
Asset

 
Domain

 
Community

 
Role In Community

 
Radio Buttons

 
Checkbox

 
Checkbox Group

 
Select (Single)

 
Select (Multiple)

 
Blank Space

 
Text Display

 
Image

 
Link

 
Horizontal Line

 
Panel

 
Subform

 
Form outcomes

 
Form expressions

 
Form scopes

 

Start forms
 

 
Configuration variables

 
Form properties

 
Form property types

 
Form values

 

Form examples
 

 
Basic concept

 
Change the state of text input components based on the checkbox selection

 
Mark a form field as mandatory if a value entered in another field meets a condition

 
Display assets only from a selected domain

 
JavaScript in expressions

 
Create a workflow with dynamic forms

 
Edit an out-of-the-box workflow

 
Change the process model properties

 

Managing workflows in Collibra
 

 
Out-of-the-box workflow deployments

 
Deploy a workflow

 
View and edit workflows

 
Enable or disable workflows

 
View and edit workflow definition settings

 
Workflows title bar

 

Configuration variables
 

 
Edit configuration variables

 
Duration variables

 
Translating workflows

 
View running workflow instances

 
System instances

 
Delete workflows

 
How to manage the new workflow permissions

 

Out-of-the-box workflows walk-throughs
 

 

Approval Process
 

 
Approval Process configuration

 

Assign Owner To Data Set
 

 
Assign Owner To Data Set configuration

 

Cancel Process
 

 
Cancel Process configuration

 

Escalation Process
 

 
Escalation Process configuration

 

Issue Creation
 

 
Issue Creation configuration

 

Issue Management
 

 
Issue Management configuration

 

Issue Move
 

 
Issue Move configuration

 

Post Data Ingestion Workflow
 

 
Post Data Ingestion Workflow configuration

 

Propose New Business Asset
 

 
Propose New Business Asset configuration

 

Propose New Business Term
 

 
Propose New Business Term configuration

 

Propose New Code Value
 

 
Propose New Code Value configuration

 

Propose New Data Asset
 

 
Propose New Data Asset configuration

 

Propose New Governance Asset
 

 
Propose New Governance Asset configuration

 

Propose New Technology Asset
 

 
Propose New Technology Asset configuration

 

Request Assets Access
 

 
Request Assets Access configuration

 

Simple Approval
 

 
Simple Approval configuration

 

Voting Sub-Process
 

 
Voting Sub-Process configuration

 
Voting Sub-Process instructions

Start
 

 
Designing workflows
 

 
Processes
 

 
Process execution
 
 

                Bulk operations in Groovy script tasks
                            

                                Beans
                

 

 

Java API v1 to v2 mapping

This section lists the changes that impact Java API v1 methods.

Interface v1

Method v1

Change

Interface v2

Method v2

ActivityStreamComponent

getActivities

Convert

ActivityStreamApi

getActivities

ApplicationComponent

executeInTransaction

Drop

 

 

ApplicationComponent

getBaseURL

Convert

ApplicationApi

getInfo

ApplicationComponent

getBuildNumber

Convert

ApplicationApi

getInfo

ApplicationComponent

getDatabaseVersion

Drop

 

 

ApplicationComponent

getFreeMemory

Drop

 

 

ApplicationComponent

getJavaHome

Drop

 

 

ApplicationComponent

getJavaInfo

Drop

 

 

ApplicationComponent

getMajorMinorVersion

Convert

ApplicationApi

getInfo

ApplicationComponent

getMaxMemory

Drop

 

 

ApplicationComponent

getOSInfo

Drop

 

 

ApplicationComponent

getStylingOverride

Drop

 

 

ApplicationComponent

getTotalMemory

Drop

 

 

ApplicationComponent

getUptime

Drop

 

 

ApplicationComponent

getUsedMemory

Drop

 

 

ApplicationComponent

getUserHome

Drop

 

 

ApplicationComponent

getVersion

Convert

ApplicationApi

getInfo

ApplicationComponent

hasDatabaseConnection

Drop

 

 

ApplicationComponent

isBootstrapped

Drop

 

 

ApplicationComponent

isCloud

Drop

 

 

ApplicationComponent

isDatabaseUpToDate

Drop

 

 

ApplicationComponent

isReportBugEnabled

Drop

 

 

ApplicationComponent

reportBug

Drop

 

 

ArticulationComponent

recalculateAllScores

Drop

 

 

AttachmentComponent

addAttachmentToResource

Convert

AttachmentApi

addAttachment

AttachmentComponent

addAttachmentToResourceFromUrl

Convert

AttachmentApi

addAttachment

AttachmentComponent

changeAttachment

Convert

AttachmentApi

removeAttachment + addAttachment

AttachmentComponent

findAttachmentByFile

Convert

AttachmentApi

findAttachments

AttachmentComponent

findAttachmentsByResource

Convert

AttachmentApi

findAttachments

AttachmentComponent

findAttachmentsByUser

Convert

AttachmentApi

findAttachments

AttachmentComponent

findFileName

Convert

FileApi

getFileInfo

AttachmentComponent

getAttachment

Convert

AttachmentApi

getAttachment

AttachmentComponent

getAttachmentContent

Convert

AttachmentApi

getAttachmentContent

AttachmentComponent

removeAttachment

Convert

AttachmentApi

removeAttachment

AttributeComponent

addAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addAttributesAsync

Convert

ImporterApi

 

AttributeComponent

addBooleanAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addDateAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addDateTimeAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addDefinition

Convert

AttributeApi

addAttribute

AttributeComponent

addDescription

Convert

AttributeApi

addAttribute

AttributeComponent

addExample

Convert

AttributeApi

addAttribute

AttributeComponent

addMultiValueListAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addNote

Convert

AttributeApi

addAttribute

AttributeComponent

addNumericAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addScriptAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addSingleValueListAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

addStringAttribute

Convert

AttributeApi

addAttribute

AttributeComponent

changeAttribute

Convert

AttributeApi

changeAttribute

AttributeComponent

changeAttributesAsync

Convert

ImporterApi

 

AttributeComponent

changeBooleanAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeDateAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeDateTimeAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeMultiValueListAttributeValues

Convert

AttributeApi

changeAttribute

AttributeComponent

changeNumericAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeScriptAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeSingleValueListAttributeValue

Convert

AttributeApi

changeAttribute

AttributeComponent

changeStringAttributeLongExpression

Convert

AttributeApi

changeAttribute

AttributeComponent

getAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getAttributeCount

Drop

 

 

AttributeComponent

getAttributesOfTypeForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getAttributesOfTypesForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getAttributesOfTypesForRepresentationInCollection

Convert

AttributeApi

findAttributes

AttributeComponent

getBooleanAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getDateAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getDateTimeAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getDefinitionsForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getDescriptionsForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getExamplesForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getHyperlinkedLongExpression

Drop

 

 

AttributeComponent

getMultiValueListAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getNotesForRepresentation

Convert

AttributeApi

findAttributes

AttributeComponent

getNumericAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getScriptAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getSingleValueListAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

getStringAttribute

Convert

AttributeApi

getAttribute

AttributeComponent

removeAttribute

Convert

AttributeApi

removeAttribute

AttributeComponent

validateConstraint

Convert

AttributeTypeApi

getAttributeType

AttributeComponent

validateMultiValueListConstraint

Convert

AttributeTypeApi

getAttributeType

AttributeComponent

validateSingleValueListConstraint

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

addBooleanAttributeType

Convert

AttributeTypeApi

addAttributeType

AttributeTypeComponent

addBooleanAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addDateAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addDateAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addDateTimeAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addDateTimeAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addNumericAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addNumericAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addScriptAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addStringAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addStringAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addValueListAttributeType

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

addValueListAttributeTypeWithCustomUUID

Convert

AttributeTypeApi

addAttributeTypes

AttributeTypeComponent

change

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeAllowedValues

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeDescription

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeIsInteger

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeKeepHistory

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeScriptLanguage

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

changeSignifier

Convert

AttributeTypeApi

changeAttributeTypes

AttributeTypeComponent

createAttributeTypeFilter

Drop

 

 

AttributeTypeComponent

findAllKeepHistoryAttributeTypesWithSignifier

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

findAttributeTypesContainingSignifier

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

getAttributeTypes

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

getAttributeType

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

getAttributeTypeBySignifier

Convert

AttributeTypeApi

getAttributeTypeByName

AttributeTypeComponent

getAttributeTypeDescription

Convert

AttributeType

getDescription

AttributeTypeComponent

getAttributeTypeKind

Convert

AttributeType

To be infered from returned object

AttributeTypeComponent

getAllowedValues

Convert

MultiValueListAttributeType

getAllowedValues

AttributeTypeComponent

getDefinitionAttributeType

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

getDescriptionAttributeType

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

getExampleAttributeType

Convert

AttributeTypeApi

findAttributeTypes

AttributeTypeComponent

getIsInteger

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

getKeepHistory

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

getNoteAttributeType

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

getScriptLanguage

Convert

AttributeTypeApi

getAttributeType

AttributeTypeComponent

getLegacyAttributeTypeKind

Drop

 

 

AttributeTypeComponent

removeAttributeType

Convert

AttributeTypeApi

removeAttributeType

BootstrapComponent

resetAuditTables

Drop

 

 

CommentComponent

addComment

Convert

CommentApi

addComment

CommentComponent

addReply

Convert

CommentApi

addComment

CommentComponent

changeComment

Convert

CommentApi

changeComment

CommentComponent

getComment

Convert

CommentApi

getComment

CommentComponent

getComments

Convert

CommentApi

findComments

CommentComponent

getCommentsByUser

Convert

CommentApi

findComments

CommentComponent

getReplies

Convert

CommentApi

findComments

CommentComponent

removeComment

Convert

CommentApi

removeComment

CommunityComponent

addCommunity

Convert

CommunityApi

addCommunity

CommunityComponent

addSubCommunity

Convert

CommunityApi

addCommunities

CommunityComponent

change

Convert

CommunityApi

changeCommunity

CommunityComponent

changeDescription

Convert

CommunityApi

changeCommunities

CommunityComponent

changeLanguage

Drop

 

 

CommunityComponent

changeName

Convert

CommunityApi

changeCommunity

CommunityComponent

changeParentCommunity

Convert

CommunityApi

changeCommunity

CommunityComponent

changeUri

Drop

 

 

CommunityComponent

exists

Convert

CommunityApi

exists

CommunityComponent

findCommunitiesContainingName

Convert

CommunityApi

findCommunities

CommunityComponent

getCommunities

Convert

CommunityApi

findCommunities

CommunityComponent

getCommunityByName

Convert

CommunityApi

findCommunities

CommunityComponent

getCommunity

Convert

CommunityApi

getCommunity

CommunityComponent

getCommunityByUri

Drop

 

 

CommunityComponent

getCommunityCount

Convert

OutputModuleApi

 

CommunityComponent

removeCommunity

Convert

CommunityApi

removeCommunity

CommunityComponent

removeCommunityJob

Convert

CommunityApi

removeCommunityInJob

CommunityComponent

removeAsync

Convert

CommunityApi

removeCommunitiesInJob

CommunityComponent

removeParentCommunity

Convert

CommunityApi

makeRootCommunity

CompareComponent

compareCurrentWithSnapshot

Drop

 

 

CompareComponent

compareSnapshotWithCurrent

Drop

 

 

CompareComponent

compareSnapshots

Drop

 

 

CompareComponent

compareViewConfigs

Drop

 

 

CompareComponent

compareVocabularyTermsBySignifier

Drop

 

 

ComplexRelationComponent

addComplexRelation

Convert

ComplexRelationApi

addComplexRelation

ComplexRelationComponent

changeComplexRelation

Convert

ComplexRelationApi

changeComplexRelation

ComplexRelationComponent

createComplexRelationFilter

Convert

FindComplexRelationsRequest

builder

ComplexRelationComponent

getComplexRelation

Convert

ComplexRelationApi

getComplexRelation

ComplexRelationComponent

getComplexRelationCount

Convert

OutputModuleApi

 

ComplexRelationComponent

getComplexRelations

Convert

ComplexRelationApi

findComplexRelation (assetId, ComplexRelationtypeId)

ComplexRelationComponent

getInvolvedComplexRelationTypes

Convert

ComplexRelationApi

findComplexRelations

ComplexRelationComponent

removeComplexRelation

Convert

ComplexRelationApi

removeComplexRelation

ComplexRelationTypeComponent

addComplexRelationType

Convert

ComplexRelationTypeApi

addComplexRelationType

ComplexRelationTypeComponent

changeComplexRelationType

Convert

ComplexRelationTypeApi

changeComplexRelationType

ComplexRelationTypeComponent

exportCSV

Convert

ComplexRelationApi

exportCSVInJob

ComplexRelationTypeComponent

exportCSVAsString

Convert

ComplexRelationApi

exportCSV

ComplexRelationTypeComponent

exportCSVWithoutJob

Convert

ComplexRelationApi

exportCSVToFile

ComplexRelationTypeComponent

exportExcel

Convert

ComplexRelationApi

exportExcelInJob

ComplexRelationTypeComponent

exportExcelWithoutJob

Convert

ComplexRelationApi

exportExcelToFile

ComplexRelationTypeComponent

getAllComplexRelationTypes

Convert

ComplexRelationTypeApi

findComplexRelationTypes

ComplexRelationTypeComponent

getComplexRelationType

Convert

ComplexRelationTypeApi

getComplexRelationType

ComplexRelationTypeComponent

remove

Convert

ComplexRelationTypeApi

removeComplexRelationType

ConceptTypeComponent

addConceptType

Convert

AssetTypeApi

addAssetType

ConceptTypeComponent

addConceptTypeWithCustomUUID

Convert

AssetTypeApi

addAssetType

ConceptTypeComponent

findConceptTypesContainingSignifier

Convert

AssetTypeApi

findAssetTypes

ConceptTypeComponent

getConceptTypes

Convert

AssetTypeApi

findAssetTypes

ConceptTypeComponent

findAllSpecializedAssetTypes

Convert

AssetTypeApi

findSubTypes

ConceptTypeComponent

findSpecializedAssetTypes

Convert

AssetTypeApi

findAssetTypes

ConceptTypeComponent

getBusinessTermType

Convert

AssetTypeApi

getAssetType

ConceptTypeComponent

getCodeTermType

Convert

AssetTypeApi

getAssetType

ConceptTypeComponent

getConceptType

Convert

AssetTypeApi

getAssetType

ConceptTypeComponent

getConceptTypeHierarchy

Convert

AssetTypeApi

findSubTypes

ConfigurationComponent

clear

Drop

 

 

ConfigurationComponent

getBoolean

Drop

 

 

ConfigurationComponent

getInteger

Drop

 

 

ConfigurationComponent

getProperty

Drop

 

 

ConfigurationComponent

getString

Drop

 

 

ConfigurationComponent

setProperty

Drop

 

 

DGCConfigurationComponent

get

Drop

 

 

FileComponent

activateFileUploadExceeding

Drop

 

 

FileComponent

addFile

Convert

FileApi

addFile

FileComponent

deactivateFileUploadExceeding

Drop

 

 

FileComponent

getFileAsStream

Convert

FileApi

getFileAsStream

FileComponent

getFileContentType

Convert

FileApi

getFileInfo

FileComponent

getFileName

Convert

FileApi

getFileInfo

FileComponent

getFileSize

Convert

FileApi

getFileInfo

FileComponent

uploadMultipartContent

Drop

 

 

ImpactComponent

createRelationTrace

Drop

 

 

ImpactComponent

getAssetRelationImpact

Drop

 

 

ImpactComponent

getAssetRelationImpactForTargetTerm

Drop

 

 

ImpactComponent

getAssetRelationImpactForTargetType

Drop

 

 

ImpactComponent

getAssetUsageRelationImpact

Drop

 

 

ImpactComponent

getAttributeReferenceImpact

Drop

 

 

ImpactComponent

getCommentReferenceImpact

Drop

 

 

ImpactComponent

getUserUsageRelationImpact

Drop

 

 

InputViewComponent

getColumnNames

Drop

 

 

InputViewComponent

importCSV

Convert

ImporterApi

importCSVInJob

InputViewComponent

importExcel

Convert

ImporterApi

importExcelInJob

InputViewComponent

importFile

Convert

ImporterApi

importCSVInJob

InputViewComponent

importTableFile

Convert

ImporterApi

importCSVInJob

InputViewComponent

simulateImportCSV

Convert

ImporterApi

importCSVInJob

InputViewComponent

simulateImportExcel

Convert

ImporterApi

importExcelInJob

InputViewComponent

simulateImportFile

Convert

ImporterApi

importCSVInJob

InputViewComponent

simulateImportTableFile

Convert

ImporterApi

importCSVInJob

IOComponent

checkTableViewConfig

Convert

OutputModuleApi

To use the validation feature set validationEnabled parameter to true when passing tableViewConfig to OutputModuleApi export... methods.

IOComponent

checkViewConfig

Convert

OutputModuleApi

To use the validation feature set validationEnabled parameter to true when passing tableViewConfig to OutputModuleApi export... methods.

IssueComponent

addIssue

Convert

IssueApi

addIssue

IssueComponent

getIssues

Convert

IssueApi

findIssues

IssueComponent

getOpenIssuesCount

Drop

 

Use the reporting functionality instead

JobComponent

cancelJob

Convert

JobApi

cancelJob

JobComponent

createJobFilter

Drop

 

 

JobComponent

getActiveJobs

Convert

JobApi

findJobs

JobComponent

getJobs

Convert

JobApi

findJobs

JobComponent

getRunningJobs

Convert

JobApi

findJobs

JobComponent

getWaitingJobs

Convert

JobApi

findJobs

JobComponent

getJob

Convert

JobApi

getJob

JobComponent

setVisibility

Drop

 

 

JobComponent

setVisibilityForFinishedJobs

Drop

 

 

JobComponent

updateNotification

Drop

 

 

LoggerComponent

debug

Convert

LoggerApi

debug

LoggerComponent

error

Convert

LoggerApi

error

LoggerComponent

info

Convert

LoggerApi

info

LoggerComponent

warn

Convert

LoggerApi

warn

MappingComponent

addMapping

Convert

MappingApi

addMapping

MappingComponent

cleanMappings

Convert

MappingApi

removeMappingsByExternalSystemInJob

MappingComponent

findMapping

Convert

MappingApi

removeMappingByMappedResource

MappingComponent

findMappingByExtEntity

Convert

MappingApi

getMappingByExternalEntity

MappingComponent

findMappingByResource

Convert

MappingApi

removeMappingByMappedResource

MappingComponent

getMapping

Convert

MappingApi

getMapping

MappingComponent

getMappings

Convert

MappingApi

findMappings

MappingComponent

removeMapping

Convert

MappingApi

removeMapping

MappingComponent

removeMappingByExtEntity

Convert

MappingApi

removeMappingByExternalEntity

MappingComponent

removeMappingByResource

Convert

MappingApi

removeMappingByMappedResource

MappingComponent

updateMapping

Convert

MappingApi

changeMapping

MappingComponent

updateMappingByExtEntity

Convert

MappingApi

changeMappingByExternalEntity

MappingComponent

updateMappingByResource

Convert

MappingApi

changeMappingByMappedResource

MetadataComponent

getSPMetadataAsString

Convert

SingleSignOnApi

getSPMetadataAsString

NavigationStatisticsComponent

findMostViewedTerms

Convert

NavigationStatisticsApi

findMostViewedAssets

NavigationStatisticsComponent

findMostViewedTermsInLastPeriod

Convert

NavigationStatisticsApi

findMostViewedAssets

NavigationStatisticsComponent

findRecentlyViewedTerms

Convert

NavigationStatisticsApi

findRecentlyViewedAssets

NounExtractorComponent

extractCandidateTermFromAttachment

Drop

 

 

NounExtractorComponent

extractCandidateTermFromFile

Drop

 

 

NounExtractorComponent

extractCandidateTermFromRepresentations

Drop

 

 

NounExtractorComponent

extractCandidateTermFromText

Drop

 

 

NounExtractorComponent

extractCandidateTermFromVocabulary

Drop

 

 

NounExtractorComponent

extractNounsFromAttachment

Drop

 

 

NounExtractorComponent

extractNounsFromFile

Drop

 

 

NounExtractorComponent

extractNounsFromRepresentations

Drop

 

 

NounExtractorComponent

extractNounsFromText

Drop

 

 

NounExtractorComponent

extractNounsFromVocabulary

Drop

 

 

OutputViewComponent

buildOutputView

Convert

OutputModuleApi

exportJSON, exportXML

OutputViewComponent

buildTableOutputView

Convert

OutputModuleApi

exportJSON, exportCSV, exportJSONToFile, exportCSVToFile, exportExcelToFile

OutputViewComponent

exportCSV

Convert

OutputModuleApi

exportCSVInJob

OutputViewComponent

exportCSVAsString

Convert

OutputModuleApi

exportCSV

OutputViewComponent

exportCSVWithoutJob

Convert

OutputModuleApi

exportCSVToFile

OutputViewComponent

exportExcel

Convert

OutputModuleApi

exportExcelInJob

OutputViewComponent

exportExcelWithoutJob

Convert

OutputModuleApi

exportExcelToFile

OutputViewComponent

exportOutputView

Convert

OutputModuleApi

exportJSONInJob, exportXMLInJob

OutputViewComponent

exportTableOutputView

Convert

OutputModuleApi

exportJSONInJob, exportCSVInJob, exportExcelInJob

OutputViewComponent

getJSONDataTable

Convert

OutputModuleApi

exportJSON

OutputViewComponent

getModelOutputView

Convert

OutputModuleApi

exportJSON

OutputViewComponent

getRelationTraceHierarchyJSONDataTable

Convert

OutputModuleApi

exportJSON

OutputViewComponent

getSingleRelationHierarchyJSONDataTable

Convert

OutputModuleApi

exportJSON

OutputViewComponent

getTableOutputView

Convert

OutputModuleApi

exportJSON, exportCSV

RelationComponent

addRelation

Convert

RelationApi

addRelation

RelationComponent

addRelationsAsync

Convert

ImporterApi

 

RelationComponent

addRelationsAsyncWithTarget

Convert

ImporterApi

 

RelationComponent

change

Convert

RelationApi

changeRelation

RelationComponent

changeEndDate

Convert

RelationApi

changeRelation

RelationComponent

changeSourceTerm

Convert

RelationApi

changeRelation

RelationComponent

changeStartDate

Convert

RelationApi

changeRelation

RelationComponent

changeTargetTerm

Convert

RelationApi

changeRelation

RelationComponent

findRelationsBySource

Convert

RelationApi

findRelations

RelationComponent

findRelationsBySourceAndTarget

Convert

RelationApi

findRelations

RelationComponent

findRelationsBySourceAndTargetAndType

Convert

RelationApi

findRelations

RelationComponent

findRelationsBySourceAndType

Convert

RelationApi

findRelations

RelationComponent

findRelationsByTarget

Convert

RelationApi

findRelations

RelationComponent

findRelationsByTargetAndType

Convert

RelationApi

findRelations

RelationComponent

findRelationsByType

Convert

RelationApi

findRelations

RelationComponent

findRelationsUsingOnlyNonNullParameters

Convert

RelationApi

findRelations

RelationComponent

getRelation

Convert

RelationApi

getRelation

RelationComponent

getRelationCount

Convert

OutputModuleApi

 

RelationComponent

hasRelationsBySourceAndType

Convert

RelationApi

 

RelationComponent

hasRelationsByTargetAndType

Convert

RelationApi

 

RelationComponent

removeRelation

Convert

RelationApi

removeRelation

RelationComponent

replaceMultipleAsync

Convert

ImporterApi

 

RelationTypeComponent

addRelationType

Convert

RelationTypeApi

addRelationType

RelationTypeComponent

addRelationTypeWithCustomUUID

Convert

RelationTypeApi

addRelationType

RelationTypeComponent

changeBinaryFactTypeWithExistingTerms

Convert

RelationTypeApi

changeRelationType

RelationTypeComponent

findPossibleRelationTypesForSourceTerm

Convert

RelationTypeApi

AssignmentApi#getAssignmentForAsset

RelationTypeComponent

findPossibleRelationTypesForSourceType

Convert

RelationTypeApi

AssignmentApi.getAssignmentsForAssetType

RelationTypeComponent

findPossibleRelationTypesForTargetTerm

Convert

RelationTypeApi

AssignmentApi#getAssignmentForAsset

RelationTypeComponent

findPossibleRelationTypesForTargetType

Convert

RelationTypeApi

AssignmentApi.getAssignmentsForAssetType

RelationTypeComponent

findRelationTypesContainingRole

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

findRelationTypesContainingRoleAndHeadOrTail

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

findRelationTypesContainingRoleOrSignifier

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

getAllRelationTypes

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

getRelationType

Convert

RelationTypeApi

getRelationType

RelationTypeComponent

getRelationTypesContainingHeadTerm

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

getRelationTypesContainingSourceTerm

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

getRelationTypesContainingTailTerm

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

getRelationTypesContainingTerm

Convert

RelationTypeApi

findRelationTypes

RelationTypeComponent

removeRelationType

Convert

RelationTypeApi

removeRelationType

RepresentationComponent

changeConceptType

Convert

AssetApi

changeAsset

RepresentationComponent

changeConceptTypesAsync

Convert

AssetApi

changeAssets

RepresentationComponent

changeExcludedFromHyperlinking

Convert

AssetApi

changeAsset

RepresentationComponent

changeStatus

Convert

AssetApi

changeAsset

RepresentationComponent

changeStatusAsync

Convert

AssetApi

changeAssets

RepresentationComponent

changeVocabulariesAsync

Convert

AssetApi

changeAssets

RepresentationComponent

changeVocabulary

Convert

AssetApi

changeAsset

RepresentationComponent

exists

Convert

AssetApi

exists

RepresentationComponent

findPossibleAttributeOrRelationTypes

Convert

AssignmentApi

getAssignmentForAsset

RepresentationComponent

findPossibleAttributeTypes

Convert

AssignmentApi

getAssignmentForAsset

RepresentationComponent

findPossibleStatuses

Convert

AssignmentApi

getAssignmentForAsset

RepresentationComponent

getRepresentation

Convert

AssetApi

getAsset

RepresentationComponent

remove

Convert

AssetApi

removeAsset

RightsComponent

addMember

Convert

ResponsibilityApi

addResponsibility

RightsComponent

addMembersAsync

Convert

ResponsibilityApi

addResponsibility

RightsComponent

addRole

Convert

RoleApi

addRole

RightsComponent

addRoleWithCustomUUID

Convert

RoleApi

addRole

RightsComponent

findRolesContainingSignifier

Convert

RoleApi

findRoles

RightsComponent

getCurrentUserRights

Convert

ResponsibilityApi

findResponsibilities (use UserApi.getCurrentUser())

RightsComponent

getGlobalRoles

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getResourceRoles

Convert

RoleApi

findRoles

RightsComponent

changeMemberRole

Convert

ResponsibilityApi

removeResponsibility, addResponsibility

RightsComponent

changeMembers

Convert

ResponsibilityApi

removeResponsibility, addResponsibility

RightsComponent

changeMembersAsync

Convert

ResponsibilityApi

removeResponsibility, addResponsibility

RightsComponent

getMember

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMemberCount

Drop

 

 

RightsComponent

getAllMemberGroupsByResourceAndRole

Convert

ResponsibilityApi

findResponsibilities & userGroupApi

RightsComponent

getAllMemberUsersByResourceAndRole

Convert

ResponsibilityApi

findResponsibilities & userApi combo

RightsComponent

getAllMembersByResource

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getAllMembersByResourceAndRole

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getInheritedMembers

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getInheritedMembersByResourceAndRole

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMemberRoles

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMembers

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMembersByOwner

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMembersByOwnerAndRole

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMembersByResourceAndRole

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getMembersByRole

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getOwners

Convert

ResponsibilityApi

findResponsibilities

RightsComponent

getRight

Convert

 

We have an enum listing all rights (com.collibra.dgc.core.api.model.security.Permission)

RightsComponent

getRightCategories

Drop

 

 

RightsComponent

getRightCategory

Drop

 

 

RightsComponent

getRights

Convert

 

We have an enum listing all rights (com.collibra.dgc.core.api.model.security.Permission)

RightsComponent

getRoleByName

Convert

RoleApi

findRoles

RightsComponent

getRoles

Convert

RoleApi

findRoles

RightsComponent

getRole

Convert

RoleApi

getRole

RightsComponent

grant

Convert

RoleApi

addRole

RightsComponent

grantCategory

Drop

 

 

RightsComponent

setPermissions

Convert

RoleApi

changeRole

RightsComponent

isAuthorized

Convert

RoleApi

isPermitted

RightsComponent

isCategoryAuthorized

Drop

 

 

RightsComponent

isComplete

Drop

 

 

RightsComponent

isPermitted

Drop

 

 

RightsComponent

isPermittedOnCommunity

Drop

 

 

RightsComponent

isPermittedOnRepresentation

Drop

 

 

RightsComponent

isPermittedOnVocabulary

Drop

 

 

RightsComponent

removeMember

Convert

ResponsibilityApi

removeResponsibility

RightsComponent

removeRole

Convert

RoleApi

removeRole

RightsComponent

revoke

Convert

RoleApi

changeRole

RightsComponent

revokeCategory

Drop

 

 

RightsComponent

searchRoles

Convert

RoleApi

findRoles

StatusComponent

addStatus

Convert

StatusApi

addStatus

StatusComponent

addStatusWithCustomUUID

Convert

StatusApi

addStatus

StatusComponent

changeDescription

Convert

StatusApi

changeStatus

StatusComponent

changeSignifier

Convert

StatusApi

changeStatus

StatusComponent

findStatusesContainingSignifier

Convert

StatusApi

findStatuses

StatusComponent

getStatus

Convert

StatusApi

getStatus

StatusComponent

getStatusBySignifier

Convert

StatusApi

getStatusByName

StatusComponent

getStatuses

Convert

StatusApi

findStatuses

StatusComponent

removeStatus

Convert

StatusApi

removeStatus

StatusComponent

updateStatus

Convert

StatusApi

changeStatus

TermComponent

addTerm

Convert

AssetApi

addAsset

TermComponent

addTerms

Convert

AssetApi

addAssets

TermComponent

changeConceptType

Convert

AssetApi

changeAsset

TermComponent

changeConceptTypesAsync

Convert

AssetApi

changeAssets

TermComponent

changeExcludedFromHyperlinking

Convert

AssetApi

changeAsset

TermComponent

changeGeneralConcept

Convert

AssetApi

changeAsset

TermComponent

changeSignifier

Convert

AssetApi

changeAsset

TermComponent

changeStatus

Convert

AssetApi

changeAsset

TermComponent

changeStatusAsync

Convert

AssetApi

changeAssets

TermComponent

changeVocabulariesAsync

Convert

AssetApi

changeAssets

TermComponent

changeVocabulary

Convert

AssetApi

changeAsset

TermComponent

exists

Convert

AssetApi

exists

TermComponent

findPossibleAttributeOrRelationTypes

Convert

AssignmentApi

getAssignmentForAsset

TermComponent

findPossibleAttributeTypes

Convert

AssignmentApi

getAssignmentForAsset

TermComponent

findPossibleStatuses

Convert

AssignmentApi

getAssignmentForAsset

TermComponent

findTermsContainingSignifier

Convert

AssetApi

findAssets

TermComponent

getRepresentation

Convert

AssetApi

getAsset

TermComponent

getRootType

Convert

AssetTypeApi

findParentTypes

TermComponent

getTerm

Convert

AssetApi

getAsset

TermComponent

getTermArticulationScore

Convert

Asset

getArticulationScore

TermComponent

getTermBySignifier

Convert

AssetApi

findAssets

TermComponent

getTerms

Convert

AssetApi

findAssets

TermComponent

getTermsCreatedCount

Drop

 

 

TermComponent

remove

Convert

AssetApi

removeAsset

TermComponent

removeAsync

Convert

AssetApi

removeAsset

TermComponent

removeGeneralConcept

Drop

 

 

TermComponent

removeTerms

Convert

AssetApi

removeAssets

TermComponent

removeTermsJob

Convert

AssetApi

removeAssets

UserComponent

addAdditionalEmail

Convert

UserApi

changeUser

UserComponent

addAddress

Convert

UserApi

changeUser

UserComponent

addGroup

Convert

UserGroupApi

addUserGroup

UserComponent

addInstantMessagingAccount

Convert

UserApi

changeUser

UserComponent

addPhone

Convert

UserApi

changeUser

UserComponent

addUser

Convert

UserApi

addUser

UserComponent

addUserToGroup

Convert

UserGroupApi

addUsersToUserGroup

UserComponent

addUsers

Convert

UserApi

addUsers

UserComponent

addUsersToGroup

Convert

UserGroupApi

addUsersToUserGroup

UserComponent

addWebsite

Convert

UserApi

changeUser

UserComponent

changeAdditionalEmail

Convert

UserApi

changeUser

UserComponent

changeAddress

Convert

UserApi

changeUser

UserComponent

changeAvatar

Convert

UserApi

changeUserAvatar

UserComponent

changeGroup

Convert

UserGroupApi

changeUserGroup

UserComponent

changeInstantMessagingAccount

Convert

UserApi

changeUser

UserComponent

changeLanguage

Convert

UserApi

changeUser

UserComponent

changePhone

Convert

UserApi

changeUser

UserComponent

changeUser

Convert

UserApi

changeUser

UserComponent

changeUserName

Convert

UserApi

changeUser

UserComponent

changeWebsite

Convert

UserApi

changeUser

UserComponent

exists

Convert

UserApi

exists

UserComponent

findGroupsContainingName

Convert

UserGroupApi

findUserGroups

UserComponent

findUsersContainingName

Convert

UserApi

findUsers

UserComponent

getCurrentUser

Convert

UserApi

getCurrentUser

UserComponent

getGroup

Convert

UserGroupApi

getGroup

UserComponent

getGroupByName

Convert

UserGroupApi

getUserGroupByName

UserComponent

getGroups

Convert

UserGroupApi

findUserGroups

UserComponent

getGroupsForUser

Convert

UserGroupApi

findUserGroups

UserComponent

getUser

Convert

UserApi

getUser

UserComponent

getUserByEmail

Convert

UserApi

getUserByEmailAddress

UserComponent

getUserByName

Convert

UserApi

getUserByUserName

UserComponent

getUserOrGroup

Convert

UserApi, UserGroupApi

getUser, getUserGroup

UserComponent

getUsers

Convert

UserApi

findUsers

UserComponent

removeAdditionalEmail

Convert

UserApi

changeUser

UserComponent

removeAddress

Convert

UserApi

changeUser

UserComponent

removeAvatar

Convert

UserApi

removeAvatar

UserComponent

removeGroup

Convert

UserGroupApi

removeUserGroup

UserComponent

removeInstantMessagingAccount

Convert

UserApi

changeUser

UserComponent

removePhone

Convert

UserApi

changeUser

UserComponent

removeUser

Convert

UserApi

removeUser

UserComponent

removeUserFromGroup

Convert

UserGroupApi

removeUserFromUserGroup

UserComponent

removeWebsite

Convert

UserApi

changeUser

UserComponent

setGroupUsers

Convert

UserGroupApi

setUsersForUserGroup

UserComponent

setUserGroups

Convert

UserApi

setGroupsForUser

ValidationComponent

createTermValidationResultFilter

Drop

 

 

ValidationComponent

getDependencies

Drop

 

 

ValidationComponent

getTermValidationInfo

Convert

ValidationApi

findValidationResults

ValidationComponent

getTermValidationResults

Convert

ValidationApi

findValidationResults

ValidationComponent

getValidationRule

Convert

AssetApi

getAsset

ValidationComponent

setDependencies

Drop

 

 

ValidationComponent

validate

Convert

ValidationApi

validate

ValidationComponent

validateAsync

Convert

ValidationApi

validateInJob

ValidationComponent

validateAsynchronous

Convert

ValidationApi

validateInJob

ValidationComponent

validateScript

Drop

 

 

VerbaliserComponent

verbalise

Drop

 

 

ViewRightComponent

addViewRightForGroup

Convert

ViewPermissionApi

addViewPermission

ViewRightComponent

addViewRightForUser

Convert

ViewPermissionApi

addViewPermission

ViewRightComponent

createViewRightFilter

Drop

 

 

ViewRightComponent

getResourcesInHierarchyWithViewRights

Drop

 

 

ViewRightComponent

getViewRight

Convert

ViewPermissionApi

getViewPermission

ViewRightComponent

getViewRights

Convert

ViewPermissionApi

findViewPermissions

ViewRightComponent

isPermitted

Convert

ViewPermissionApi

 

ViewRightComponent

removeViewRight

Convert

ViewPermissionApi

removeViewPermission

VocabularyComponent

addVocabulary

Convert

DomainApi

addDomain

VocabularyComponent

change

Convert

DomainApi

changeDomain

VocabularyComponent

changeCommunity

Convert

DomainApi

changeDomain

VocabularyComponent

changeDescription

Convert

DomainApi

changeDomain

VocabularyComponent

changeExcludedFromHyperlinking

Convert

DomainApi

changeDomain

VocabularyComponent

changeName

Convert

DomainApi

changeDomain

VocabularyComponent

changeNameAndUri

Convert

DomainApi

changeDomain

VocabularyComponent

changeType

Convert

DomainApi

changeDomain

VocabularyComponent

changeUri

Drop

 

?

VocabularyComponent

exists

Convert

DomainApi

exists

VocabularyComponent

findPossibleAttributeOrRelationTypes

Convert

AssignmentApi

getAvailableRelationTypes, getAvailableComplexRelationTypes, getAvailableAttributeTypes

VocabularyComponent

findPossibleAttributeTypes

Convert

AssignmentApi

getAvailableAttributeTypes

VocabularyComponent

findPossibleComplexRelationTypes

Convert

AssignmentApi

getAvailableComplexRelationTypes

VocabularyComponent

findPossibleFactTypes

Convert

AssignmentApi

getAvailableRelationTypes

VocabularyComponent

findPossibleObjectTypes

Convert

AssignmentApi

getAvailableAssetTypesForDomain

VocabularyComponent

findPossibleRelationTypes

Convert

AssignmentApi

getAvailableRelationTypes

VocabularyComponent

findPossibleStatuses

Drop

 

 

VocabularyComponent

findVocabulariesContainingName

Convert

DomainApi

findDomains

VocabularyComponent

getNonMetaVocabularies

Convert

DomainApi

findDomains

VocabularyComponent

getNumberOfTerms

Convert

OutputModuleApi

 

VocabularyComponent

getTerms

Convert

AssetApi

findAssets

VocabularyComponent

getVocabularies

Convert

DomainApi

findDomains

VocabularyComponent

getVocabulariesByCommunity

Convert

DomainApi

findDomains

VocabularyComponent

getVocabulariesByName

Convert

DomainApi

findDomains

VocabularyComponent

getVocabulariesByType

Convert

DomainApi

findDomains

VocabularyComponent

getVocabulariesByTypeAndCommunity

Convert

DomainApi

findDomains

VocabularyComponent

getVocabulary

Convert

DomainApi

getDomain

VocabularyComponent

getVocabularyByUri

Drop

 

 

VocabularyComponent

getVocabularyCount

Convert

OutputModuleApi

 

VocabularyComponent

removeAsync

Convert

DomainApi

removeDomainInJob

VocabularyComponent

removeVocabulariesJob

Convert

DomainApi

removeDomainsInJob

VocabularyComponent

removeVocabulary

Convert

DomainApi

removeDomain

VocabularyTypeComponent

addVocabularyType

Convert

DomainTypeApi

addDomainType

VocabularyTypeComponent

addVocabularyTypeWithCustomUUID

Convert

DomainTypeApi

addDomainType

VocabularyTypeComponent

getAllSpecializedVocabularyTypes

Convert

DomainTypeApi

findSubTypes

VocabularyTypeComponent

findVocabularyTypeByName

Convert

DomainTypeApi

findDomainTypes

VocabularyTypeComponent

findVocabularyTypesContainingSignifier

Convert

DomainTypeApi

findDomainTypes

VocabularyTypeComponent

getAllSpecializedVocabularyTypes

Convert

DomainTypeApi

findSubTypes

VocabularyTypeComponent

getCodeVocabularyType

Drop

 

 

VocabularyTypeComponent

getGlossaryVocabularyType

Drop

 

 

VocabularyTypeComponent

getVocabularyType

Convert

DomainTypeApi

getDomainType

VocabularyTypeComponent

getVocabularyTypeHierarchy

Drop

 

 

VocabularyTypeComponent

getVocabularyTypes

Convert

DomainTypeApi

findDomainTypes

VocabularyTypeComponent

findPossibleConceptTypes

Drop

 

 

WorkflowComponent

addAssignmentRule

Convert

WorkflowDefinitionApi

addAssetTypeAssignmentRule

WorkflowComponent

cancelWorkflow

Convert

WorkflowInstanceApi

cancelWorkflowInstance

WorkflowComponent

cancelWorkflowWithTask

Convert

WorkflowTaskApi

cancelWorkflowTask

WorkflowComponent

change

Convert

WorkflowDefinitionApi

changeWorkflowDefinition

WorkflowComponent

change

Convert

WorkflowDefinitionApi

changeWorkflowDefinition

WorkflowComponent

changeAssignmentRule

Convert

WorkflowDefinitionApi

changeAssetTypeAssignmentRule

WorkflowComponent

changeItemResourceType

Convert

WorkflowDefinitionApi

changeWorkflowDefinition

WorkflowComponent

changeStartEvents

Convert

WorkflowDefinitionApi

changeWorkflowDefinition

WorkflowComponent

completeTask

Convert

WorkflowTaskApi

completeWorkflowTasks

WorkflowComponent

completeTaskForGuestUser

Convert

WorkflowTaskApi

completeWorkflowTasks

WorkflowComponent

completeTasks

Convert

WorkflowTaskApi

completeWorkflowTasks

WorkflowComponent

createTaskFilter

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

deploy

Convert

WorkflowDefinitionApi

deployWorkflowDefinition

WorkflowComponent

findProcessInstances

Convert

WorkflowInstanceApi

findWorkflowInstances

WorkflowComponent

findWorkflowDefinitionsByName

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getAllProcessInstances

Convert

WorkflowInstanceApi

findWorkflowInstances

WorkflowComponent

getAllProcessInstances

Convert

WorkflowInstanceApi

findWorkflowInstances

WorkflowComponent

getAllTasks

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasks

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForCommunity

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForCommunity

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForUser

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForUser

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForVocabulary

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAllTasksForVocabulary

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasks

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasks

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForCommunity

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForCommunity

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForGuestUser

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForGuestUser

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForVocabulary

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getAssignedTasksForVocabulary

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getConfigurationStartFormData

Convert

WorkflowTaskApi

getConfigurationStartFormData

WorkflowComponent

getGlobalWorkflowDefinitions

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getPossibleStartEvents

Convert

WorkflowDefinitionApi

getPossibleWorkflowStartEventTypes

WorkflowComponent

getProcessInstances

Convert

WorkflowInstanceApi

findWorkflowInstances

WorkflowComponent

getProcessInstancesByItem

Convert

WorkflowInstanceApi

findWorkflowInstances

WorkflowComponent

getStartFormData

Convert

WorkflowTaskApi

getStartFormData

WorkflowComponent

getTask

Convert

WorkflowTaskApi

getWorkflowTask

WorkflowComponent

getTaskActivityFilter

Convert

WorkflowTaskApi

getFindActivitiesRequestForTask

WorkflowComponent

getTaskActivityStream

Convert

ActivityStreamApi

getActivities

WorkflowComponent

getTaskFormData

Convert

WorkflowTaskApi

getTaskFormData

WorkflowComponent

getTasks

Convert

WorkflowTaskApi

findWorkflowTasks

WorkflowComponent

getWorkflowDefinition

Convert

WorkflowDefinitionApi

getWorkflowDefinition

WorkflowComponent

getWorkflowDefinitionByProcessId

Convert

WorkflowDefinitionApi

getWorkflowDefinitionByProcessId

WorkflowComponent

getWorkflowDefinitions

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getWorkflowDefinitionsForCommunities

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getWorkflowDefinitionsForRepresentations

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getWorkflowDefinitionsForVocabularies

Convert

WorkflowDefinitionApi

findWorkflowDefinitions

WorkflowComponent

getWorkflowDiagram

Convert

WorkflowDefinitionApi

getWorkflowDefinitionDiagram

WorkflowComponent

getWorkflowInstanceDiagram

Convert

WorkflowInstanceApi

getWorkflowInstanceDiagram

WorkflowComponent

getWorkflowXML

Convert

WorkflowDefinitionApi

getWorkflowDefinitionXML

WorkflowComponent

getWorkflowXMLContent

Convert

WorkflowDefinitionApi

getWorkflowDefinitionXML

WorkflowComponent

getWorkflowXMLName

Convert

WorkflowDefinitionApi

getWorkflowDefinitionXML

WorkflowComponent

messageEventRecieved

Convert

WorkflowInstanceApi

messageEventReceived

WorkflowComponent

reassignTask

Convert

WorkflowTaskApi

reassignTask

WorkflowComponent

remove

Convert

WorkflowDefinitionApi

removeWorkflowDefinition

WorkflowComponent

removeAssignmentRule

Convert

WorkflowDefinitionApi

removeAssignmentRule

WorkflowComponent

removeAsync

Convert

WorkflowDefinitionApi

removeWorkflowDefinitionsInJob

WorkflowComponent

setConfigurationVariables

Convert

WorkflowDefinitionApi

changeWorkflowDefinition

WorkflowComponent

startWorkflow

Convert

WorkflowInstanceApi

startWorkflowInstances

WorkflowComponent

startWorkflowForUser

Convert

WorkflowInstanceApi

startWorkflowInstances

WorkflowComponent

startWorkflows

Convert

WorkflowInstanceApi

startWorkflowInstances

WorkflowComponent

startWorkflowsAsychronously

Convert

WorkflowInstanceApi

startWorkflowInstancesInJob

WorkflowComponent

startWorkflowsAsync

Convert

WorkflowInstanceApi

startWorkflowInstancesInJob

                Bulk operations in Groovy script tasks
                            

                                Beans
                

 

 

X

LinkedIn

Instagram

YouTube

About Collibra

Collibra Platform

Blog

Careers

Partner Program

Contact us

Sitemap

© 2026 Collibra. All rights reserved.

Privacy and legal

