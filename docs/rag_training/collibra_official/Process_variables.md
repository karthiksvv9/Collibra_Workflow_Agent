# Process variables

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/co_process-variables.htm

 

Process variables

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
 

 
Creating workflows
 

 
Workflow basic configuration elements
 
 

                Workflow description
                            

                                Workflow dialog boxes
                

 

 

Process variables

September 24, 2025

Variables play a critical role in workflows by dynamically storing and passing data. This enables workflows to adapt to user input, system states, or external data.

Variables act as placeholders for data that you can dynamically assign, modify, or retrieve during the execution of a workflow. They allow workflows to respond to specific conditions, user inputs, or system states, making workflows more flexible and interactive.

For example, a variable can store:

User input from a form, such as a due date entered by a user.

Dynamic data retrieved from Collibra assets, such as the name of an asset.

System-generated values, such as timestamps or IDs.

Setting process variables

Process variables originate from various sources:

The start event initiator
: The value you provide as the 
Initiator
 variable of the 
start event
 becomes one of the first variables, defining the user who starts the workflow. By default, the value is 
initiator
 and user tasks are automatically assigned to this candidate through the expression 
user(${initiator})
.

User task form fields
: In user tasks, any data entry or selection component that a user interacts with becomes a process variable. You use the 
Value
 property of the component to reference this variable.

Script task
 variables
:
The scope of the variables you declare in a script task is limited to that script. However, you can set process variables, which become available outside the script, using 
execution.setVariable(<variable_name>, <varaible_value>);
, where 
<variable_name>
 is a 
String
 and 
<variable_value>
 is an 
object
.
Workflow 
beans
: Built-in context variables that provide information about the context in which the workflow is running, such as 
users.current
 or 
item.type
.
API interfaces: Interfaces such as 
AssetApi
, 
UserApi
, and 
FileApi
 are pre-instantiated and accessible via variables such as 
assetApi
, 
userApi
, and 
fileApi
.

Configuration variables
: When you deploy a workflow, Collibra automatically adds a series of default configuration variables for each user task. These include 
duration variables
 for the due dates and escalation durations, in addition to any configuration variables you might have set.

Reserved variable names

When working with variables in workflows, it is important to be aware of reserved variable names. These are predefined variables that Collibra uses, and they cannot be overridden or redefined in your workflows. Using these reserved names for custom variables can lead to unexpected behavior or errors:

escalationType

event

eventResourceId

eventResourceType

eventTaskCandidates

eventTaskId

eventTaskKey

eventType

eventV1

eventV2

initiator

isApiV2Workflow

item

itemCommunity

itemResourceId

itemResourceType

itemV1

itemV2

itemVocabulary

mail

users

usersV1

usersV2

workflowDefinitionName

workflowStartUserId

Retrieving process variables

You can retrieve process variables in several ways, depending on where this action occurs:

In script tasks
: You have direct access to all process variables. You can also explicitly retrieve a variable with 
execution.getVariable(<variable_name>);
, where 
<variable_name>
 is a 
String
.

In other process components
: Use JUEL expressions to access variables, such as 
${myVariable}
.

In form components
: Unless otherwise noted, retrieve the value of a variable by including the variable name in a form expression: 
{{}}
, for example 
{{initiator}}
.

Exchanging process variables with a sub-process

Sub-processes are workflows that run as part of a parent workflow. They are not designed to be stand-alone workflows. You must provide values for start form variables with the 
Required
 property set to 
true
. Additionally, you may use sub-process variables in the parent workflow.

To exchange information between a parent workflow and a sub-process, configure the 
call activity
 in the parent workflow:

In the 
In
 section of the 
Variable Mapping
 properties, add items and:
Enter parent workflow process variables in the 
Source variable
 field.
Enter the corresponding sub-process variables in the 
Target variable
 field.
Use an expression in the 
Source Expression
 field if to pass a hard-coded value, for example 
${"Enter a brief description"}
 or 
${false}
.

In the 
Out
 section of the 
Variable Mapping
 properties, add items and:
Enter sub-process variables in the 
Source variable
 field.
Enter the corresponding parent workflow process variables in the 
Target variable
 field.

Since the parent workflow and the sub-process are separate workflows, you can use the same name for corresponding variables.

Important considerations

By understanding and leveraging variables effectively, you can create dynamic and responsive workflows in Collibra that cater to a wide range of business needs.

To maximize the potential of variables, consider the following:

Descriptive naming
: Use clear and meaningful names, such as 
requestorName
 instead of 
rn
.

Consistent naming conventions
: Follow consistent patterns, for example camel case: 
usageRequestReason
.

Scope and data type awareness
: Understand where variables are accessible and their data types.

Variable validation
: Implement validation where necessary to ensure data integrity.

                Workflow description
                            

                                Workflow dialog boxes
                

 

 

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

