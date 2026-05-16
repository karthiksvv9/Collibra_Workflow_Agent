# Overview of execution listeners

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/Listeners/co_execution-listeners.htm

 

Overview of execution listeners

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
 
 

                Overview of task listeners
                            

                                Logging in workflows
                

 

 

Overview of execution listeners

 Deprecated Java Core API v1 listeners  will be discontinued in the near future for improved stability and security. Use Java Workflow API v2 listeners where available or script tasks to replace the functionality of v1 listeners. See 
Alternatives to API v1 listeners
 for examples.

FlushExecutionListener
: This listener exists for a pure technical reason. When everything is executed in one transaction, data is not always flushed to the database in between. For example if you create assets in a workflow and right after that you want to add some relations, this will not work. The newly created assets are detected by the workflow logic and adding the relations fails, unless you add this execution listener in between. For more information about transaction boundaries in a workflow please refer to the 
Flowable documentation
 and search for 
Transactions and Concurrency
.

AuthCacheEvictExecutionListenerr
: This listener clears the authorization cache of the current user and flushes all changes made during the current session. Clearing the cache can be useful when the authorization cache needs to be updated immediately, even before the transaction is committed. Typically, the cache is updated only after the transaction is committed. For example, you can have a script task assign a user to a group with the necessary permissions to participate in the workflow and immediately assign the same user to the next task. Without this listener, the user does not have the appropriate permissions to be assigned to a task until the transaction is committed. With the listener, the cache that stores the user permissions is refreshed prior to assigning the task. An alternative approach is to make the script asynchronous, but this prevents the user task from being opened automatically.

SendEscalationEventExecutionListener
: Listener that triggers an escalation event. By default the escalation process is listening to these events to start it's execution. You can use this listener to trigger a escalation event yourself. It needs two input parameters:
Field name
Expressions
Mandatory
Description
taskId
N
Y
The ID of the task the escalation is for.
escalationType
N
N
The type of the escalation. This variable is used in the escalation process to determine which kind of escalation to execute. 
The default is 
mail
 so this is a optional parameter.

SetMembersExecutionListener
: A listener to easily set members on the current workflow business item. It has three input fields:
Field name
Expressions
Mandatory
Description
userNames
Y
Y
A CSV of usernames you want to set a member for.
roleName
Y
Y
The name of the role. You can only specify one role to use at once.
clearExisting
N
Y
If 
true
 all existing members on the current business item will be deleted prior to adding new. If empty no clearing is performed.

SetActivityStreamListener
: A listener capable of setting the filter which will be used to generate a activity stream. This listener is both a execution listener and a task listener. The filter it generates will be put in a local variable. This means, in the case of a usertask, the variable will only exist as long as the task exists. Outside of a user task, the variable will exist for the current execution only, meaning it will not be visible in super or sub process instances. You can decide for yourself if you want it to be used as a tasklistener or execution listener on user tasks.
				
When the listener has been used, a user will be able to see a activity stream on the task bar. Also, when action mails are send, the configured activity stream can be included in the action mails for the current user task. There are a lot of configuration options which we will discuss next.
			Here is the list of all input fields. None of them are mandatory and if no input is provided, all changes since the start of the workflow on the current resource are listed.
Field name
Expressions
Mandatory
Description
user
Y
N
Limits to only show activities for the user with the given user name. Needs to be a username.
role
Y
N
Filter only the changes where the user, specified in the 
user
 parameter has a given role in. If no user is given, only the changes are returned performed by users having the given role.
involvedUser
Y
N
Only show activities where the given user is involved in/has a role in.
involvedRole
Y
N
Filter only the changes where the user, specified in the 
involvedUser
 parameters, has a given role in.
startTimeEmpty
N
N
This will override the default: the start time is the beginning of the current workflow, meaning all activities since the beginning of time will be shown.
startTask
N
N
The task ID of the task to take as start timestamp to show activities for.
startOnStatusChangeFrom
N
N
Fill in the signifier of the status here if you want all activities to show since the latest status change from the given status.
endTask
N
N
Sets the end timestamp to the given task ID.
resourceTypes
N
N
 Filter on the types to return the changes for. If empty or null, all resource types are taken into account.

                Overview of task listeners
                            

                                Logging in workflows
                

 

 

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

