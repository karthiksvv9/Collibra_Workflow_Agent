# Workspaces

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/co_workspaces.htm

 

Workspaces

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
 
 

                Designing workflows
                            

                                Models
                

 

 

Workspaces

March 13, 2026

Workspaces in Workflow Designer are essential for organizing your workflow models, particularly for large projects or managing multiple distinct workstreams.

Workspaces provide a dedicated area to group and manage your workflow models. This structure allows you to create workspaces tailored to your specific needs, helping to keep different projects or development efforts clearly separated and organized.

Your Workflow Designer must have at least one workspace. The out-of-the-box workspace name is 
Generated default
.

Workspaces offer several features to enhance how you manage your workflow development:

Improved project organization: You can create distinct workspaces for different projects or initiatives. This helps maintain a clear and focused modeling environment while providing flexibility through the ability to move apps or copy app versions between workspaces.

Tailored environments: The ability to create workspaces as needed means you can set up an organizational structure that best fits your development processes.

Default workspace: You can designate one workspace as the default. This can streamline your access to your most frequently used or primary set of workflow apps and models.

Efficient navigation: The Workspaces page allows you to filter and sort your workspaces. This makes it easier to quickly find and navigate to the specific workspace you need, especially as the number of your projects grows.

By using these workspace features, you can maintain a more organized and efficient workflow development process.

Find and view workspaces

As you create more workspaces, the Workspaces page provides several options to help you efficiently locate and view them.

Search: Use the search to find workspaces or jump to recently visited models.

Filter by name: Enter part or all of a workspace name to narrow down the list of workspaces.

View options: Click 
 
View options
 to open the controls for changing how workspaces are shown:
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

Create a workspace

You can create new workspaces to organize your workflow models according to your project needs.

Steps

In the navigation bar, select 
Workspaces
.

On the Workspaces page, click 
 
Create
.

In the 
Create a new workspace
 dialog box, enter the required information:
        
        
Field
Description
Name
The name for your workspace. This name helps you identify the workspace and its purpose.
Key
The unique identifier of the workspace. By default, the Workflow Designer auto-generates the key from the workspace name. Alternatively, you can specify a custom key.
Description
Optionally, a description of the workspace. You can use the formatting options for bold, italics, or monospace.
Visibility
Whether the workspace is public or private. A public workspace is visible to all users. A private workspace is visible only to users with explicit access.

Click 
Create
.

Your new workspace is created and appears on the Workspaces page. You can now select this workspace to start adding or managing workflow apps and models in it.

Manage workspaces

After you create workspaces, you can modify their properties, visibility, set one as default, or remove those you no longer need.

To perform these actions, access the actions menu:

On the Workspaces page, find the workspace and click the 
 more icon next to it.

From an individual workspace page, click 
 
Actions
 next to the name of the workspace in the navigation menu.

Edit workspace details

From the actions menu, click 
Edit workspace
.

In the 
Update the workspace
 dialog box, update any of the following:
        
Name
: Change the display name of the workspace.
Key
: Modify the unique key of the workspace.
Description
: Update the descriptive text of the workspace.

Click 
Ok
 to apply your changes.

Change workspace visibility

From the actions menu, click 
Change visibility
.

In the 
Change visibility
 dialog box, select one of the following:
        
Public
: The workspace is visible to all users.
Private
: The workspace is visible only to you and users with explicit access.

Click 
Save
 to apply your changes.

Change workspace permissions

A private workspace is visible only to you. You can manage access to your workspace and define user roles through workspace permissions:

From the actions menu, click 
Change permissions
.

In the 
Change workspace permissions
 dialog box, configure the following options:
        
Users
: Select who has access to the workspace.
Type
: Select the role to assign to each user:
Owner
: Has full access to the workspace and the  apps and models it contains, including the ability to edit, change visibility, or remove the workspace.
Modeler
: Can create and edit apps and models.
Reader
: Can view the workspace and the  apps and models it contains.

Click 
Save
 to apply your changes.

Set a default workspace

From the actions menu of the desired workspace, select 
Set as default
.

The selected workspace is now your default workspace.

Remove a workspace

If you no longer need a workspace and the items it contains, you can remove it.

Removing a workspace is a permanent action that also deletes all workflow apps and models from that workspace. Ensure you no longer need the workspace, apps, and models before proceeding.

Steps

From the actions menu, select 
Remove workspace
.

In the 
Delete the workspace
 dialog box, click 
Delete the workspace
 to confirm that you want to remove the workspace.

The workspace and the associated workflow apps and models are deleted.

                Designing workflows
                            

                                Models
                

 

 

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

