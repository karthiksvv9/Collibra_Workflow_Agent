# Process editor

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Process/to_process-editor.htm

 

Process editor

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
 
 

                Import processes
                            

                                Process editor menu bar
                

 

 

Process editor

March 23, 2026

You use the process editor to create BPMN diagrams. It allows you to visually model your processes using a drag-and-drop mechanism.

Page overview

The process editor main page is divided into four areas:

The 
menu bar
 on top, just below the navigation bar.

The 
Shape repository
 on the left side.

The 
canvas
 in the middle.

The properties bar on the right side.

General properties

Property

Description

Model Key

The unique identifier of the process in both Workflow Designer workspaces and  Collibra. The key must be unique in any given workspace and in your Collibra environment.

Name

The name of the process, which becomes the display name of the workflow in Collibra.

Documentation

The workflow description that is shown in Collibra, providing details about the purpose and general usage of a workflow.

Assignment properties

Property

Description

Owner

The owner of the instances of the process. This option is not currently used in Collibra.

Details properties

Property

Description

Author

The owner of the instances of the process. This option is not currently used in Collibra.

Version

A manual free-form field used to add versions to your workflows according to your needs. This is for informational purposes only and is different from automatic 
model versions
 or 
app revisions
.

Signal definitions

Definition of the signals that the process uses, comprised of:
Model Id
: A unique ID of the signal event.
Name
: The name of the signal event, used to reference it later.
Scope
: Whether all process instances can listen for this signal event, or only listeners within the same process instance.

Message definitions

Definition of the messages that the process uses, comprised of:
Model Id
: A unique id of the message event.
Name
: The name of the message event, used to reference it later.

Advanced properties

Property

Description

Event listeners

Event listeners of this process, which react to a series of predefined low-level runtime events that are fired during process instance execution:
Event
: The type of event that the listener should listen to.
Delegate expression
: The expression to be executed when the process is started. A delegate expression must resolve to a Java object, for instance a Spring bean. The object's class must implement either 
JavaDelegate
 or 
ActivityBehavior
.
Class
: The fully qualified classname of a class to be invoked when executing the process, for example 
com.collibra.dgc.workflow.api.listener.FlushExecutionListener
.
Entity type
: The type of entity that should be targeted by events for which the event-listener should be notified, which allows to filter the events that are received by this listener.
Rethrow event
: Whether to rethrow the event that is recieved.
Rethrow event type
: The type of the event that is thrown: 
error
, 
message
, 
signal
, or 
globalSignal
.
Rethrow event name
: The name under which the error, message or signal is thrown.

Data objects

A list of process variables that are initialized when the process instance is started:
ID of the data object
: A unique identifier of the data object.
Name
:The name of the variable, used to reference it later.
Type
: The data type of the variable.
Default value
: An optional default value for the variable.

Execution listeners

Allows you to invoke Java logic after certain events:
Start
: Executes after the activity has been started.
End
: Executes after the activity was completed.

                Import processes
                            

                                Process editor menu bar
                

 

 

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

