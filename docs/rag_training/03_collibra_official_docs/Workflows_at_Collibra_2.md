# Workflows at Collibra

Source: https://developer.collibra.com/workflows/workflow-documentation

 

Workflows at Collibra

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
 
 

                                About the Workflow Designer
                

 

 

Workflows at Collibra

November 28, 2025

Collibra workflows are automated business processes that guide users through a series of steps to achieve specific data governance objectives. They are fundamental to ensuring consistency, efficiency, and compliance across your data landscape.

Whether you are an administrator configuring your Collibra environment or a developer building custom solutions, workflows are central to how work gets done in Collibra.

A Collibra workflow represents a defined sequence of activities, tasks, and decisions that automate and enforce data governance policies and procedures. Workflows transform manual and often ad-hoc processes into structured, repeatable, and auditable flows, offering distinct advantages such as:

Automation: They automate complex data-related processes, reducing manual effort and potential for human error.

Guidance: They guide users through required steps, ensuring all necessary information is provided and proper approvals are secured.

Enforcement: They enforce data governance policies, such as checking for data quality, assigning data ownership, or providing compliance approvals.

Integration: They can interact with assets, attributes, and relations, and also integrate with external systems.

Auditing: They can log every step and decision within a workflow, providing a clear audit trail for compliance and reporting.

Key capabilities and use cases

Collibra workflows are highly versatile and can be tailored to a wide range of use cases:

Manage data request and approval processes:
Request access to data assets.
Approve new data definitions or changes to existing ones.
Onboard new data sources or datasets.

Automate data quality and stewardship:
Route data quality issues to relevant data stewards for resolution.
Initiate cleansing processes based on data profiling results.
Assign data ownership or stewardship roles.

Enforce policy and compliance:
Ensure data privacy regulations, such as GDPR and CCPA, are followed for sensitive data.
Trigger legal or security reviews for high-risk assets.
Manage data retention policies.

Streamline operational tasks:
Send automated notifications or reminders.
Create new assets, domains, or communities programmatically.
Update asset properties based on external events.

Integrate with external systems:
Trigger processes in external applications, such as ticketing systems or ETL tools, based on workflow events.
Receive data from external systems to update Collibra assets.

How workflows work

Workflows orchestrate interactions between users, the Collibra platform, and potentially external systems.

You often get to interact with workflows through:

Tasks: Specific actions assigned to one or more users.

Forms: Dialog boxes where you provide information or make a decision, often pre-populated with relevant data from the platform.

Notifications: Automated emails or messages that inform you about new tasks or workflow status changes.

Email tasks: Custom emails that are sent to you as part of a workflow email task.

Workflows start depending on their configuration:

Manually: You start a workflow from an asset page, a community, a dashboard, or the global 
Create
 button.

Following an event: Workflows start automatically when specific events occur in Collibra, such as the creation of a new asset, a change in an attribute value, or the addition of a relation.

Scheduled: Some workflows are configured to run at specific intervals.

Users interact with workflows by completing tasks in their individual task lists or directly on asset pages, which moves the process forward. Administrators monitor the status of running workflows and manage workflow instances.

How workflows are built

Collibra workflows use an industry-standard Business Process Management Notation (BPMN 2.0) engine. This engine enables both visual modeling and running and managing complex processes.

As a workflow designer, you interact with the following tools and elements:

Workflow Designer: A visual tool that allows you to design and model workflows using standard and custom elements:
Start and end events
: Define the beginning and end of a process.
User tasks
: Represent points where human interaction is required.
Service and API tasks
: Automate actions performed by the workflow engine, such as calling Collibra APIs or external REST services.
Script tasks
: Run custom Groovy code for complex logic, data manipulation, or specific Collibra interactions.
Gateways
: Control the process flow based on conditions, such as exclusive or parallel gateways.
Forms
: Design user forms, allowing you to link form fields to workflow variables and Collibra attributes.

Variables
: Store information used throughout the workflow.

Java APIs
: Workflows connect with Collibra  through APIs, enabling actions such as:
Reading and writing asset information, including attributes and relations.
Creating, updating, or deleting assets.
Listening for and responding to Collibra events.
Managing user permissions and roles.

Listeners
: Components that respond to specific workflow events, such as task creation or workflow completion, to perform additional actions.

Once designed, you deploy workflows to your Collibra environment, where they are available for configuration and execution.

                                About the Workflow Designer
                

 

 

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

