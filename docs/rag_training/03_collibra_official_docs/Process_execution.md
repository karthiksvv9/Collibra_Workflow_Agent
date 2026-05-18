# Process execution

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/co_process-execution.htm

 

Process execution

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
 
 

                Canvas and configuration area
                            

                                The workflow user
                

 

 

Process execution

The workflow engine executes the process in a transactional way, advancing until it encounters a wait state, such as a timer event, in each active path of the execution. Subsequent tasks, sub-processes, and call activities are executed in a single transaction, and if one fails, the entire transaction is rolled back.

Asynchronous activities

You can have tasks, sub-processes, and call activities run asynchronously to split execution into smaller units of work. The benefit of an asynchronous activity is that it is part of a separate transaction, and if it fails, the actions that were performed before it are not rolled back.

The Workflow Designer provides two independent properties to control where transaction boundaries are placed around an activity:

Asynchronous

Places a transaction boundary 
before
 the activity starts. The activity runs in a separate background thread, isolated from the steps that preceded it.

Leave asynchronously

Places a transaction boundary 
after
 the activity completes, before the process advances to the next element. This ensures the completed state is committed immediately, preventing the activity from being re-run if the engine restarts.

The following table summarizes how these properties affect transaction boundaries:

Setting

Transaction break point

Effect

Neither property set.

None.

Fastest execution. The activity runs in the same transaction as its surrounding steps. If it fails, the entire transaction is rolled back.

Asynchronous
 set.

Before the activity starts.

The activity runs in a background thread. A failure does not roll back the steps that ran before it.

Leave asynchronously
 set.

After the activity completes.

The completed state is committed before the process moves on. The activity is not re-run.

Synchronous script tasks are attributed to the user who starts the task. Asynchronous script tasks are attributed to the 
workflow user
.

Notwithstanding the above, the type of actions that the scripts invoke determine whether Collibra checks for permissions or not:

If the script invokes synchronous calls, such as 
domainApi.removeDomain
 or 
workflowInstanceApi.startWorkflowInstances
, the actions are performed within the workflow context. The users who start the task do not need roles with permissions that allow the task to complete.

If the script invokes asynchronous calls, such as 
importerApi.importExcelInJob
 or 
domainApi.removeDomainInJob
, the jobs run outside of the workflow context. The users who start the task need roles with permissions that allow the task to complete.

To perform actions as a specific user, use the 
runAsUserById()
 or 
runAsUserByUserName()
 methods of the 
Users
 bean
.

Exclusive activities

By default, all activities run as exclusive jobs and cannot be completed at the same time as another exclusive activity that belongs to the same process. This ensures the workflow engine performs all activities sequentially. You do not need to change this behavior, as the built-in capabilities can manage different scenarios. You can learn more about the logic behind exclusive jobs in the 
Flowable documentation
.

                Canvas and configuration area
                            

                                The workflow user
                

 

 

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

