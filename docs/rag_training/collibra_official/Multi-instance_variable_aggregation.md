# Multi-instance variable aggregation

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/co_variable-aggregations.htm

 

Multi-instance variable aggregation

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
 
 

                Logging in workflows
                            

                                Shape repository
                

 

 

Multi-instance variable aggregation

September 15, 2025

Multi-instance workflow executions allow a task or subprocess to be executed repeatedly, either sequentially or in parallel, for a dynamic number of items in a collection. A common use case is collecting input from multiple participants, such as reviewers providing feedback on a document or application.

By default, variables created or updated in each individual instance of a multi-instance execution are confined to a local scope. This prevents data clashes but makes it difficult to consolidate outputs from multiple instances into a single variable for subsequent use. The 
Variable Aggregations
 feature automates this process, enabling the collection, consolidation, and transformation of data from multi-instance executions efficiently.

Configuring variable aggregations

The 
Variable Aggregations
 feature is available in the 
Multi instance
 properties group of process elements that support multi-instance executions. It allows you to configure one or more aggregation definitions, mapping variables from individual executions to a single, structured target variable.

The configuration includes the following options:

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

Important considerations

The options for 
Target variable creation
 and the overarching variable retention policy represent important aspects of how data is handled in multi-instance loops.

The options for creating the target variable offer distinct behavioral patterns with significant implications for process design:

Default behavior: The 
Default
 option is straightforward and mirrors a common "map-reduce" pattern. The data from all individual instances is collected, but the final, aggregated variable is not created until the entire multi-instance loop has completed. This behavior is ideal for scenarios where the aggregated data is only needed for a subsequent task that requires a complete dataset, such as making a final decision after all review feedback has been collected.

Enabling dynamic and real-time workflows with the 
Create overview variable
 option: Unlike the 
Default
 option, the 
Create overview variable
 option creates an overview variable at the very start of the multi-instance loop. This variable is continuously updated in real-time as each individual execution completes, allowing a parent process or even other concurrent child executions to access the current, partial state of the aggregated data. For example, a subprocess might use a completion condition that dynamically inspects the overview variable and terminates the loop as soon as a certain threshold is met, such as reaching a combined score of 
250
 or receiving three 
Approved
 comments. This capability transforms the multi-instance pattern from a static data collection mechanism into a dynamic coordination tool that allows the process to react to partial results, leading to more adaptive and efficient workflows.

When variable aggregation is enabled, only data specified in the aggregation is retained after the multi-instance execution is completed. All other locally-scoped variables are discarded. This policy promotes a cleaner, more efficient process instance variable space by preventing clutter. To prevent data loss, ensure that all required data is explicitly defined in the variable 
Definitions
.

Expressions in aggregation

Variable definitions support expressions, such as 
${my_expression}
, allowing for data transformations during aggregation.  This centralizes data transformation logic in the process element, reducing the need for separate script or service tasks.

Example of aggregating feedback from multiple reviewers

Consider a review process with a user task that collects the input of reviewers, each with a name and a score weight. The task is executed for each reviewer in the collection, allowing them to provide a score and a comment.

Multi-instance setup:
Multi instance type
: 
Parallel
.
Collection
: This expression points to the collection variable created in a previous task, for example 
${reviewers}
.
Element variable
: A temporary variable referencing the current item in the collection, such as 
reviewer
.

Variable Aggregations:
Target
: 
reviews
.
Type
: 
Default
.
Target variable creation
: 
Default
.

Definition that maps the 
comment
 variable from the local instance to the 
comment
 key in the final JSON object.:
Source
: 
comment
.

Definition that uses an expression to transform data. It multiplies the locally-scoped 
score
 by the 
scoreWeight
 from the 
reviewer
 element variable and divides by 100 to get a weighted score. This calculated value is then stored under the 
score
 key in the final JSON object:
Source
: 
${score * reviewer.scoreWeight / 100}
.
Target
: 
score
.

Definition that maps the  name of the reviewer from the 
reviewer
 element variable to the 
reviewer
 key in the final JSON object:
Source
: 
${reviewer.name}
.
Target
: 
reviewer
.

After all executions are completed, the aggregated variable 
reviews
 contains a JSON array with the consolidated data:
[
    { "comment": "Application looks good", "score": 90.0, "reviewer": "Jane" },
    { "comment": "Application looks perfect", "score": 80.0, "reviewer": "Jake" }
]

Conclusion

The 
Variable Aggregations
 feature simplifies process models by automating data consolidation and transformation. It eliminates the need for manual workarounds, reduces development effort, and minimizes errors. By centralizing logic in the process element, it promotes readability, maintainability, and scalability in workflows.

                Logging in workflows
                            

                                Shape repository
                

 

 

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

