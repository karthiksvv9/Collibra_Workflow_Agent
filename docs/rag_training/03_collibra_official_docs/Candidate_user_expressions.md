# Candidate user expressions

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/co_candidate-user-expressions.htm

 

Candidate user expressions

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
 

 
User task
 
 

                User task
                            

                                Service task
                

 

 

Candidate user expressions

A candidate user is a user who can perform a workflow task. You can specify candidate users by using candidate user expressions, such as 
role(Business Steward)
, 
user(John)
, or 
group(Data Custodians)
.

You can include  a comma or other punctuation marks, except semicolon, in your candidate user expressions. If you use punctuation marks, you must enclose the user expressions in curly brackets, for example 
{role(Business Steward; Community, Inc)}
.

It is best practice to use curly brackets for all user expressions, whether the user expression contains a punctuation mark or not. 

In Workflow Designer, add the candidate user expression and use 
Enter
 to confirm each entry. You can add multiple expressions.

When using a variable to store candidate user expressions, ensure the value is a String representation of one or more comma separated expressions, for example 
{user(John)}, {user(Eliza)}, {group(Data Custodians)}

Expression

Description

role(<roleName>)

Assigns the task to users with the specified role on the workflows business item. In case of a global workflow, you can use global role names.

{role(Business Steward)}
 assigns the task to users with the 
Business Steward
 role.

role(<roleName>;<communityName>)

Assigns the task to users with the specified role on the specified community. This is independent of the current workflow business item.

{role(Business Steward;Sales Community)}
 assigns the task to users with the 
Business Steward
 role in the 
Sales
 community.

This expression includes any inherited responsibilities.

role(<roleName>; <communityName>; <domainName>)

Assigns the task to users with the specified role on the domain with the specified name in the given community. This is independent of the current workflow business item.

{role(Business Steward;Sales Community;Pre Sales)}
 assigns the task to users with the 
Business Steward
 role on the 
Pre Sales
 domain in the 
Sales
 community.

This expression includes any inherited responsibilities.

role(<roleName>;<entityLevel>)

Assigns the task to users with a role on the workflow business item, but only if they have the role on the specified level. Possible entity levels are Term, Vocabulary and Community, which respectively indicate roles to be on the Asset, Domain or Community level.

{role(Business Steward;Term)}
 assigns the task to users with the 
Business Steward
 role on the asset.

role(<roleName>;<relationName>)

Assigns the task to users with the specified role on assets that are related to the current workflow business item with the given relation name.

{role(Stakeholder;Complies To)}
 assigns the task to stakeholders of assets that are related by the 
Complies To
 relation.

role(<roleName>; <entityLevel>; <relationName>)

A combination of the role(<roleName>; <entityLevel>) and role(<roleName>; <relationName>) expressions. This expression assigns the task to users of the target-related asset with a role on the given entity level. 

{role(Stakeholder; Term; Complies to)}
 assigns the task to stakeholders on the 
Asset
 level of assets that are related by the 
Complies to
 relation.

user(<userName>)

Assigns the task to the user with the specified name.

{user(John)}
 assigns the task to John.

group(<groupName>)

Assigns the task to the users in the specified group.

{group(Data Custodians)}
 assigns the task to the users in the 
Data Custodians
 group.

                User task
                            

                                Service task
                

 

 

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

