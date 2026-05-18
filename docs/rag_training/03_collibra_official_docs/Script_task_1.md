# Script task

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowDesigner/Process/ref_activities_script_task.htm

 

Script task

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
 
 

                AddComment delegate
                            

                                Manual task
                

 

 

Script task

A task that is executed by a business process engine to mainly perform simple calculations or operations. When the task is ready to start, the engine executes the script, and marks it as completed when the script has finished.

To configure script tasks, you must provide a script in Groovy language.

Because each script task is independent, include 
import
 statements for all the packages you are using in a script for each script task. Avoid using generic imports to reduce execution time. 

            Do not use script tasks to declare methods that a subsequent script task would use. Groovy compiles and temporarily caches the script at execution time. If you call the method in a subsequent script tasks:

The cached method might not be available anymore.
Even if the method is available, it retains the cached values of variables, which might lead to unexpected results.
Use the 
groovy-lib
 folder to store scripts that are common to a large number of tasks.

In the context of workflow script tasks, the 
<Resource>Api
 interfaces (such as AssetApi, CommunityTypeApi, FileApi, and so on) are already instantiated and accessible via 
<resource>Api
 variables (such as assetApi, communityTypeApi, fileApi, and so on).

General properties

Property

Description

Model ID

The unique identifier of the element within the process model.

Name

The name of the element displayed in the diagram.

Documentation

A description and any additional information about this element.

Script

A script that is executed when the task is activated.

Variable mapping properties

Property

Description

In

Optional input mapping of  variables from the current process or expressions to  script variables:
Source variable
: The name of the process variable that holds the value you want to map to a script variable.
Source expression
: A  hard-coded value for the script variable as a JUEL expression, for example 
${false}
.
Target variable
: The name of the script variable.

Multi instance properties

Property

Description

Multi instance type

                        Determines if multiple instances of this activity are created:
None
 (default): Only one instance is created.
Parallel
: Activities are created in parallel. This is good practice for user tasks.
Sequential
: Activities are created sequentially. This is good practice for service tasks.

Collection

Expression to set the loop collection for a multi-instance task. The number of instances is determined by the elements of a collection. For each element in the collection, a new instance is created.

A common use case is to loop over lists created by multi-element subforms. For example, if you bound a subform to an array of invoice positions using the expression 
invoicePositions
, you can set the loop collection to 
${invoicePositions}
 to loop over each position.

Element variable

The name of the variable where the currently processed item from the loop collection is stored, for example 
invoicePosition
.

You can access the element in the process through an expression, for example 
${invoicePosition}
. To access the element in a form, you can add a task listener that copies the variable on creation from the execution level to a local task variable, for example 
${task.setVariableLocal("invoicePosition",invoicePosition)}
. The element is then available in the form through the 
task.invoicePosition
 variable.

Element index variable

The name of the variable where the index of the currently processed item from the loop collection is stored, for example, 
itemIndex
.

The index starts with 0 and increases with every element that is being looped through. You can access the index in the process through an expression, for example 
${itemIndex}
 in the process. To access the index in a form,  you can add a task listener that copies the variable on creation from the execution level to a local task variable, for example 
${task.setVariableLocal("itemIndex", itemIndex)}
. The index is then available in the form through the 
 task.itemIndex
 variable.

Cardinality

A number or an expression that evaluates to an integer, which controls the number of activity instances that are created. If the attribute 
Collection
 is empty, a new instance is created for every element of the list. With cardinality, you can overwrite this and only create a given number of instances. You can also use this attribute if you want to loop over an activity a given number of times without specifying a collection.

Completion condition

A Boolean expression that when 
true
 cancels the remaining activity instances, stopping the loop, and produces a token.

Variable Aggregations

This option is applicable when the multi-instance type is either parallel or sequential. It automates the collection, consolidation, and transformation of data from multiple  variables created or updated in each individual instance of a multi-instance execution.

Target
: The name of the final variable that contains the aggregated data or an expression that resolves to a variable name at runtime. The aggregated variable is typically a JSON array. All variable definitions from the same aggregation contribute to a single target variable.

Type
: The method used for aggregation:
Default
: Uses the out-of-the-box aggregation logic, which is suitable for most use cases.
Custom
: Allows for advanced aggregation logic by specifying a 
Delegate Expression
 or a 
Class
 that implements the 
VariableAggregator
 interface. This option provides an extension point for highly specific requirements.

Target variable creation
: A predefined list of options that determine when and how the target variable is created and persisted:
Default
: Creates the target variable as a normal, persisted process variable only after all multi-instance executions are completed. This is the standard behavior for a "map-reduce" pattern.
Create overview variable
: Creates the variable at the start of the multi-instance loop and is continuously updates it as each child instance is completed. This allows for real-time access to the aggregated data by any running process instance. The final variable created is a normal, persisted JSON variable.
Store as transient variable
: Creates the target variable upon completion of all instances, similar to the 
Default
 option, but as a non-persisted or transient variable. This data is not saved to the process history and is suitable for temporary or intermediate data that is not needed for auditing or long-term storage.

Definitions
: A list of definitions that map source variables from each multi-instance execution to a target variable key in the final aggregated collection. For each definition, you specify a key-value pair that to be included in the JSON object representing the aggregated data:
Source
: The input data, as variable name or expression.
Target
: The key under which the source data is stored in the final JSON array. If the target name is identical to the source variable, the target is optional.

Advanced properties

Property

Description

Asynchronous

Whether the activity starts as an asynchronous job, placing a transaction boundary before the activity:
No
 (default): Synchronous.
Yes, exclusive
: Asynchronous and with no other exclusive asynchronous jobs in the same process run at the same time.
Yes, non-exclusive
: Asynchronous and can run concurrently with other asynchronous jobs in the same process.

Leave asynchronously

Whether the activity leaves as an asynchronous job after it completes, placing a transaction boundary before the process advances to the next element:
No
 (default): Synchronous.
Yes, exclusive
: Asynchronous and with no other exclusive asynchronous jobs in the same process run at the same time.
Yes, non-exclusive
: Asynchronous and can run concurrently with other asynchronous jobs in the same process.

Skip expression

An expression which is evaluated before executing the task. If it evaluates to 
true
, the task is skipped.

You must opt-in to enable this feature by setting a process variable 
_FLOWABLE_SKIP_EXPRESSION_ENABLED
 with the Boolean value 
true
.

Execution listeners

Allows you to invoke Java logic after certain events:

Start
: Executes after the activity has been started.

End
: Executes after the activity was completed.

Transition
: When defined on a sequence flow, executes once the flow is transition is taken.

Visual properties

Property

Description

Font size

The font size of the element in the diagram.

Font weight

The font weight of the element in the diagram.

Font style

The font style of the element in the diagram.

Font color

The font color of the element in the diagram.

Background color

The background color of the element in the diagram.

Border color

The border color of the element in the diagram.

                AddComment delegate
                            

                                Manual task
                

 

 

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

