# Bulk operations in Groovy script tasks

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/co_bulk-operations-groovy-script-tasks.htm

 

Bulk operations in Groovy script tasks

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
 
 

                Adjusting for Groovy JavaBeans specification compatibility changes
                            

                                Java API v1 to v2 mapping
                

 

 

Bulk operations in Groovy script tasks

When a Groovy script task calls the Collibra 
<Resource>Api
 interfaces, such as 
assetApi
, 
relationApi
, 
attributeApi
, or 
responsibilityApi
, those calls invoke Spring service beans directly rather than making HTTP requests. All of these beans use the Spring default transaction propagation, which means they join the existing transaction rather than opening their own.

A synchronous script task therefore runs entirely in a single database transaction. Every API call made during the script, including reads and writes, participates in that transaction, which stays open until the script completes.

Impact of bulk operations on transaction management

A script that iterates over a large dataset and writes for each item accumulates all those writes in one transaction. The open transaction holds row-level locks on every row it touches. Under concurrent load, other processes attempting to read or modify the same rows are blocked behind those locks. If the script runs long enough, the lock contention can saturate the database connection pool and make Collibra unresponsive.

Setting script tasks to 
Asynchronous
 alone does not resolve this issue. The task is moved to a background job thread, but the transaction boundary is unchanged and the entire script still runs in one transaction.

Recommended pattern for bulk operations

To avoid long-running transactions, split the workflow into two script tasks connected by a loop-back gateway:

A 
collector script task
 that runs synchronously in one short transaction. It queries the full dataset, builds a list of work items, and stores it as a process variable using 
execution.setVariable("workItems", ...)
.

A 
processor script task
 in asynchronous mode, which gives each execution its own transaction. It takes the first batch of items from 
workItems
, processes them, updates the process variable with the remaining items, and sets 
execution.setVariable("hasMoreWork", !workItems.isEmpty())
.

An 
exclusive gateway
 that routes back to the processor task when 
${hasMoreWork}
 is true, or proceeds to the end event when 
${!hasMoreWork}
 is true.

The following diagram illustrates this pattern:

Each time the async job executor picks up the processor task, it runs in its own transaction. A failure in one batch rolls back only that batch, and the remaining work continues.

Choosing a batch size

A batch of 25 to 50 items is a practical starting point. Smaller batches result in shorter transactions and less lock contention. Larger batches reduce job executor overhead but increase the risk of contention under concurrent load.

Alternative: parallel multi-instance subprocess

You can wrap the processor in an asynchronous subprocess with the 
Multi instance type
 property set to 
Parallel
 to process all batches in parallel, which increases throughput. However, all batch jobs compete for database connections simultaneously. Under high concurrent load, this approach may be counterproductive. Use the sequential loop-back pattern unless throughput is a critical requirement.

                Adjusting for Groovy JavaBeans specification compatibility changes
                            

                                Java API v1 to v2 mapping
                

 

 

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

