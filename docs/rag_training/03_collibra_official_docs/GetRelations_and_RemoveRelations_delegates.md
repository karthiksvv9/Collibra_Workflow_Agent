# GetRelations and RemoveRelations delegates

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/ref_getremoverelation-delegate.htm

 

GetRelations and RemoveRelations delegates

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
 

 
Shape repository
 

 
Service task
 

 
Delegates
 
 

                Alternatives to API v1 delegates
                            

                                AddRelation delegate
                

 

 

GetRelations and RemoveRelations delegates

The 
GetRelations
 and 
RemoveRelations
 delegate respectively gets and removes relations that can be identified by ID or source, term and type. Affected relations are returned with output variable.

Field name

Mandatory

Description

relationId

N

Id of the relation.

sourceTermId

N 

Id of the source term of the relation.

targetTermId

Id of the target term of the relation.

binaryFactTypeId 

Id of the BinaryFactType, this is the ID of the relation type.

resourceVariableName

N

The name of the variable that the result will be set in, if not given the result will be set in the variable named "output"

The delegate is deprecated. Replace your service task containing this delegate with a script task, for example:

Get relations:
        
<scriptTask id="scripttask1" name="Remove relation" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;        
        def relations = relationApi.findRelations(FindRelationsRequest.builder()
            .sourceId(item.id)
            .build())
        .getResults();
        execution.setVariable("output", relations)
    ]]></script>
</scriptTask>

Remove relations:
        
<scriptTask id="scripttask1" name="Remove relation" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;        
        def relations = relationApi.findRelations(FindRelationsRequest.builder()
            .sourceId(item.id)
            .build())
        .getResults();
        relationApi.removeRelations(new ArrayList(relations.collect{ it.getId() }));
    ]]></script>
</scriptTask>

                Alternatives to API v1 delegates
                            

                                AddRelation delegate
                

 

 

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

