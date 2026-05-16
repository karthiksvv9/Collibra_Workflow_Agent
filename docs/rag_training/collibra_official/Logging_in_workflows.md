# Logging in workflows

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/co_logging.htm

 

Logging in workflows

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
 
 

                Overview of execution listeners
                            

                                Multi-instance variable aggregation
                

 

 

Logging in workflows

August 19, 2025

Incorporating logging into your Collibra workflows provides valuable insights during development and execution. Logging is particularly beneficial for debugging script tasks. By strategically placing log statements at various stages of your scripts, you can:

Monitor progress: Track the execution flow and identify the current stage of a script.

Identify errors: Pinpoint the specific location where an error might be occurring.

Observe data values: Inspect the values of variables and data being processed at different points in the script.

This practice helps you diagnose issues quickly and understand the behavior of complex logic in your workflows.

General logging capabilities

Workflows use the Java 
loggerApi
 interface for writing messages to the 
dgc.log
 file, which is available in Collibra Console. The interface offers four methods, each corresponding to a specific severity level:

error(String message)
: Logs critical errors that prevent execution.

warn(String message)
: Logs potential issues that do not stop execution but may require attention.

info(String message)
: Logs general operational information and status updates.

debug(String message)
: Logs detailed, low-level information, typically used during active debugging.

By default, the 
dgc.log
 file is configured to capture log entries up to the INFO level. This means that messages logged with ERROR, WARN, and INFO are recorded. Log statements at the DEBUG level are not recorded by default. This configuration helps manage log volume, as DEBUG logs can be very verbose, especially in production environments.

Temporarily enabling DEBUG logging for enhanced debugging

When debugging a workflow script, you may need more detailed information than what is captured at the INFO level. You can temporarily elevate the logging level to DEBUG for 
loggerApi
 in Collibra Console. This allows you to use DEBUG statements in your workflow code without permanently increasing log volume.

Prerequisites

You have at least the ADMIN role in Collibra Console.

Steps

Open Collibra Console.
Collibra Console opens with the 
Infrastructure
 page.

In the tab pane, expand an environment to show its services.

Select the 
Data Governance Center
 service.

Select 
Logs
 → 
 
Settings
 → 
Add logger
.
The 
Add logger
 dialog boxappears.
 

Enter the required information:
Logger name: 
com.collibra.dgc.core.api.component.LoggerApiImpl
Logger level: 
DEBUG

Click 
Add logger
 to apply the changes and close the dialog box.

Important considerations and best practices

Impact: Changing the log level affects all workflows and services using this logger. A significant increase in logged information may occur.

Revert changes: After completing your debugging session, revert the log level to the default INFO setting or remove the custom logger entry. To do this, go to the same 
Logs
 settings page and either remove (
) the entry for 
com.collibra.dgc.core.api.component.LoggerApiImpl
 or change (
) the associated level back to INFO.

Environment: You should temporarily enable DEBUG logging only in non-production environments. This practice ensures you maintain control over log volume and avoid impacting users or system performance in a production environment.

Permanent DEBUG statements: You can include DEBUG-level log statements in your workflow code permanently. These statements are only captured when the logger level is set to DEBUG in the Collibra Console, ensuring your code remains debug-ready without causing excessive logging under normal operations.

Implementing logging in your workflows

You can integrate logging directly into your workflow logic in several ways:

In script tasks.
Script tasks are a common place to embed logging. You can add log statements at any point within your script and you can include multiple 
loggerApi
 calls in a single script task to trace the execution path and variable states.
loggerApi.info("Starting script task script_1. Value for variable myVariable is: " + execution.getVariable("myVariable"));

Via an execution listener.        
If you need to log information when the workflow reaches or completes a specific step, a separate script task solely for logging that might be inefficient. Instead, you can incorporate an execution listener directly into most process elements.
To configure an execution listener for logging, edit the process in Workflow Designer:
On the canvas, select the desired process element, for example a user task or service task.
In the properties bar, go to 
Advanced
 → 
Listeners
 → 
Execution listeners
.
In the 
Execution listeners
 dialog box, click 
 to add an execution listener.
Configure the listener by defining the event that triggers the listener and the script or expression to execute.
Event: 
Start
Type: 
Expression
Value: 
${loggerApi.debug("Sample log line")}
This approach enables granular logging tied to specific workflow events without the overhead of additional, dedicated script tasks.

Conclusion

By leveraging 
loggerApi
, you can monitor and debug workflows in Collibra with greater precision. Follow best practices, such as enabling DEBUG logging only in non-production environments and reverting settings after debugging. Properly implemented logging not only enhances development efficiency but also improves the maintainability of your workflows.

                Overview of execution listeners
                            

                                Multi-instance variable aggregation
                

 

 

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

