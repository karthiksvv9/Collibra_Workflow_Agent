# The "groovy-lib" folder

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/WorkflowElements/co_groovy-lib.htm

 

The "groovy-lib" folder

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
 
 

                Names and unique names in workflows
                            

                                Upgrading your scripts for Collibra 2024.02 compatibility
                

 

 

The "groovy-lib" folder

The 
groovy-lib
 folder is a specific directory in your Collibra environment customization files that allows you to deploy and share Groovy scripts across multiple workflow processes.

By placing Groovy scripts in this folder, you can create custom libraries and helper classes that are accessible to any workflow script task. This promotes code reusability, simplifies maintenance, and helps to enforce consistent behavior in your workflows:

Reusability

Write a function once and call it from any workflow. This saves time and reduces the chance of errors.

Maintainability

Update a script in one place, and the changes are automatically reflected in all workflows that use it.

Consistency

Ensure that common tasks, such as sending notifications or integrating with an external system, are performed in the same way everywhere.

Simplicity

Keep your workflow definitions cleaner and more focused on the business process by moving complex code logic into external libraries.

When to use the "groovy-lib" folder

You should use the 
groovy-lib
 folder when you have Groovy code that you want to reuse across different workflows or when you want to separate complex logic from your business process definitions. Some examples include:

Utility classes with helper methods for string manipulation, date calculations, or API interactions.

Standardized methods for logging or error handling.

Connectors for integrating with external systems.

For code that is specific to a single workflow and not intended for reuse, you can continue to write it directly in the workflow script tasks. The core value of the groovy-lib folder is to store scripts that are common to a large number of tasks.

Uploading scripts to the "groovy-lib" folder

To get started with the 
groovy-lib
 folder, use the console export file mechanism to add a customization package to Collibra. The workflow engine automatically makes any GROOVY files from the 
groovy-lib
 available in your workflow scripts.

Create a console export file with customizations.
Open Collibra Console with a user profile that has at least the 
ADMIN
 role.
Collibra Console opens with the 
Infrastructure
 page.
In the main menu, click 
Console Export Files
.
The Console Export Files page appears.
Above the table, to the right, click 
Create Console Export File
.
In the 
Create Console Export File
 dialog box, enter the required information:
Environment
The Collibra environment for which to create an export file.
Customizations
This ensures that if there is a 
groovy-lib
 folder it gets downloaded and allows you to upload a new or modified one.
The configuration is always included in export files for consistency and reliability.
Click 
Create Export File
.

Once Collibra finishes processing the file, download it.

Extract the contents of the archive.

Add your Groovy scripts to 
dgc
 → 
groovy-lib
.
If this folder structure does not exist, create it.

Go to the containing directory of the extracted files, select all of them, and add then to a ZIP archive.
Do not archive the containing directory. Select only the individual files and directories to have the same structure as the original ZIP file.

Upload ZIP archive to your Collibra environment:
                
Open Collibra Console with a user profile that has at least the 
ADMIN
 role.
Collibra Console opens with the 
Infrastructure
 page.
In the main menu, click 
Console Export Files
.
The Console Export Files page appears.
Above the table, to the right, click 
Upload Console Export File
.
In the 
Upload Console Export File
 dialog box, enter the required information:
Not password protected
The option to choose for new console export files.
Retain for
The retention period for the export file, after which the file is automatically removed.
Select the ZIP archive you created.
The upload starts automatically.

Once the upload finishes, apply the console export file:
In the row of the export file you have uploaded, click 
Apply Restore
.
In the 
Applying console export file
 dialog box, enter the required information:
Environment
The Collibra environment where you want to apply the export file.
Export
The export file you have uploaded.
Customizations
This ensures that the 
groovy-lib
 folder and your reusable scripts get applied.
Click 
Apply console export file
.
The console export file is applied to the selected environment. The time to apply an export file depends on the amount of data it contains. During this time, your environment is unavailable. The process is complete when all services in your environment have the running status again.

Using the "groovy-lib" folder

If you use the 
groovy-lib
 mechanism to create reusable functions across workflows, consider that by default, the entire content of the 
groovy-lib
 folder is included in each script task before compilation. Since compilation time increases with the number of lines of code, including unused reusable functions can negatively affect performance.

To mitigate this issue, enable the 
Don’t attach Groovy libs by default
 option in Collibra Console. For scripts that require reusable functions, explicitly add a 
// #importFile
 statement at the beginning of the script to load the relevant files:
// #importFile resourcePrinter.groovy
// #importFile processDetailsPrinter.groovy

Rules for using 
#importFile
:

The 
#importFile
 statement must be the first line in the script, even before the imports section. Any whitespace character at the beginning of the script is ignored.

Whitespace characters are allowed before and after 
//
.

There cannot be any whitespace character between 
#
 and 
importFile
.

Whitespace characters are allowed between 
#importFile
 and the Groovy file name.

If a referenced Groovy file is not found in the 
groovy-lib
 folder, it is silently ignored.

Additional resources

Create a console export file

Download a console export file

Upload a console export file

Apply a console export file

Script task performance

                Names and unique names in workflows
                            

                                Upgrading your scripts for Collibra 2024.02 compatibility
                

 

 

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

