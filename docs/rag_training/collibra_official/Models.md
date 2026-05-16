# Models

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/to_models.htm

 

Models

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
 
 

                Workspaces
                            

                                Apps
                

 

 

Models

March 23, 2026

Workflow Designer uses models to refer to the different building blocks of a workflow:

Model

Description

Process

A business process diagram that uses the Business Process Model and Notation (BPMN) standard.

Form

A form presenting or requesting information that a workflow users interacts with.

Find and view models

Every workspace and app has a 
Models
 page where you can see the models associated with the workspace or the app, with various options to help you efficiently locate and view your workflow models:

Filter by name: Enter part or all of a model name to narrow down the list of models.

View options: Click 
 
View options
 to open the controls for changing how models are shown:
View: Select 
List view
 or 
Grid view
 to change the layout.
Sort: Choose to sort by 
Name
 or 
Key
, and in 
Ascending
 or 
Descending
 order.

Filter by tags: Filter models by one or more tags.

Add models

The 
 
Create
 button on the 
Models
 page of a workspace or app allows you to:

Create new workflow models from scratch by defining their basic properties.

Import existing workflow definitions from BPMN or XML files or forms from FORM files.

Include models from other workflows or other workspaces into your current app, allowing for reuse and consolidation of forms and processes.

You can also create a form or process from the 
Actions
 section of the search bar.

Manage models

After you added models, you can manage them by modifying their properties, downloading definitions, tracking their usage, starring them for quick access, or removing them when they are no longer needed.

On the 
Models
 page of a workspace or an app, locate the desired model.

Click the 
 more icon next to it.
            
A drop-down menu appears with available actions:
Action
Description
Edit
Opens the model in the process form designer for modifications, in the 
Editing
 page.
Download
Downloads the model file to your local machine. This is useful for backup, version control, or sharing outside of the Workflow Designer.
Properties
Opens a dialog box where you can view and edit the model metadata, including the name, key, tags, and description.
You must open the model in an app to modify the model key.
Usage
Shows a list of other processes, forms, or apps where the selected model is currently being used. This is a critical feature for understanding dependencies before making changes or removing a model.
Star model
 Marks the model as a favorite, making it easier to visually find it.
Remove
Deletes the model permanently from the Workflow Designer.
Removing a model is a permanent action. If the model is referenced or used in any other processes, form, or application, the removal causes errors or breaks functionality in those dependent items. Always check the usage of a model before removing it.

Model versions

Whenever you save a process or a form, Workflow Designer automatically creates a new version of the form. This helps you track the evolution of your workflow models throughout their development, compare different versions, and revert to a previous version if necessary.

Model versions are different from 
app revisions
, which are manual workflow app at a specific point in time with the included models and model versions.

Manage versions

You can view, compare and restore a previous version of a process or form from the model 
Editing
 page by clicking 
 the version explorer icon:

View: Select a past model version.
            
A preview of the selected version appears.

Compare:
Click the 
Compare with version
 button.
Select any two versions to visually compare.
Differences are highlighted in green for added elements, yellow for modified elements, and red for deleted elements.

Restore a previous version:
            
Click the 
Revert to this version
 button.
In the 
Revert this model
 dialog box, click 
Accept
 to confirm the change and close the version explorer.
A new version of the model is created based on the selected past version.

                Workspaces
                            

                                Apps
                

 

 

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

