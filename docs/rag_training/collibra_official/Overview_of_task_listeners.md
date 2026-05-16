# Overview of task listeners

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/Listeners/co_task-listeners.htm

 

Overview of task listeners

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
 

 
Listeners
 
 

                Alternatives to API v1 listeners
                            

                                Overview of execution listeners
                

 

 

Overview of task listeners

 Deprecated Java Core API v1 listeners  will be discontinued in the near future for improved stability and security. Use Java Workflow API v2 listeners where available or script tasks to replace the functionality of v1 listeners. See 
Alternatives to API v1 listeners
 for examples.

ActionMailSender
: Sends workflow action emails for the task that this task listener is configured for. Only simple tasks are possible without required form input except buttons.               
Field name
Mandatory
Description
template
N
The name of the template that should be used to generate the email.
section
N
The name of the section that should be used to generate the mail.
grouped
Y
The option to send the action mail grouped or not, by default this option is 
false
.
subject
Y
The subject of the action mail to be send for non-grouped email.
executeIfTrue
Y
The option to send the action email (
true
) or not (
false
).
includeActivityStream
Y
The option to include the activity stream in the email (
true
) or not (
false
)
includeAttributes
Y
The option to include the attributes in the email (
true
) or not (
false
).
includeRelations
Y
The option to include the relations in the email (
true
) or not (
false
).
relationTypes
only if includeRelations is true
A comma separated list of relation types to be shown in the email.
If the file is empty, all relation types corresponding to the matching assignment groups are displayed.
attributeTypes
only in includeAttributes is true
A comma separated list of attribute types to be shown in the email. 
If the file is empty, all attribute types corresponding to the matching assignment groups are displayed.

CheckMandatoryFieldCombinationTaskListener
: Checks if the configured combination of form property input fields have at least one value field filled in. If not a error message will be shown to the user.
Field name
Expressions
Mandatory
Description
formFields
N
Y
A CSV of form property ids to do the mandatory check on.

SetFormSubtitleTaskListener
: This sets a given string value as the subtitle for the form to be displayed on the task. With this you can tweak the form presented to the user with custom subtitles.
Field name
Expressions
Mandatory
Description
subtitle
Y
Y
The string value for the form subtitle

SetRoleResourceTaskListener
: This provides the possibility to override the business item that is used to determine the users with given roles scoped for a certain task. Useful when you want to evaluate candidate user expression against another resource than the current workflow business item.
Keep in mind that this can make the candidate user check fail as it will only check on the current business item and will not take this listener into account. When using this listener disable the check on the workflow configuration page.
Field name
Expressions
Mandatory
Description
resourceId
Y
Y
The id of the new resource
resourceType
Y
Y
The String representation of the new resource type e.g. TE for term.

SetValueTaskListener
: Sets a variable in the workflow context. It can be used to evaluate expressions or user expressions and store the parsed value in a task LOCAL variable. This means as soon as you exit the current user task, the variable will not be available anymore.
Field name
Expressions
Mandatory
Description
valuesExpression
Y
Y 
(if userExpression is not used)
An expression that will be evaluated.
userExpression
Y
Y 
(if valuesExpression is not used)
User expressions that you want to have evaluated.
resultVariable
N
Y
The name of the variable for the result to be restored in

                Alternatives to API v1 listeners
                            

                                Overview of execution listeners
                

 

 

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

