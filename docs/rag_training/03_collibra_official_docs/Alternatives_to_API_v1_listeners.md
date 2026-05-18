# Alternatives to API v1 listeners

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/Listeners/ref_deprecated-listeners.htm

 

Alternatives to API v1 listeners

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
 

 
Listeners
 
 

                Listeners
                            

                                Overview of task listeners
                

 

 

Alternatives to API v1 listeners

This section provides examples of alternatives to Java Core API v1 listeners.

ActionMailSender

API v1

com.collibra.dgc.core.workflow.activiti.tasklistener.ActionMailSender

API v2

com.collibra.dgc.workflow.api.listener.ActionMailSender

CheckMandatoryFieldCombinationTaskListener

API v1

com.collibra.dgc.core.workflow.activiti.tasklistener.CheckMandatoryFieldCombinationTaskListener

API v2

com.collibra.dgc.workflow.api.listener.CheckMandatoryFieldCombinationTaskListener

RunAsExecutionListener

Using this listener is erroneous and causes inconsistencies in the activity stream.
It is removed without providing a replacement.

RunAsReleaseExecutionListener

Using this listener is erroneous and causes inconsistencies in the activity stream.
It is removed without providing a replacement.

SendEscalationEventExecutionListener

API v1

com.collibra.dgc.core.workflow.activiti.executionlistener.SendEscalationEventExecutionListener

API v2

com.collibra.dgc.workflow.api.listener.SendEscalationEventExecutionListener

SetActivityStreamListener

API v1

com.collibra.dgc.core.workflow.activiti.listener.SetActivityStreamListener

API v2

com.collibra.dgc.workflow.api.listener.SetActivityStreamListener

SetFormSubtitleTaskListener

API v1

com.collibra.dgc.core.workflow.activiti.tasklistener.SetFormSubtitleTaskListener

API v2

com.collibra.dgc.workflow.api.listener.SetFormSubtitleTaskListener

SetMembersExecutionListener

API v1

com.collibra.dgc.core.workflow.activiti.executionlistener.SetMembersExecutionListener

API v2

com.collibra.dgc.workflow.api.listener.SetResponsibilitiesExecutionListener

SetRoleResourceTaskListener

API v1

<userTask id="userTask1" name="usertask1" activiti:candidateUsers="user(Admin), role(Normal), role(Business Steward), role(Community Manager)">
    <extensionElements>
        <activiti:taskListener event="create" class="com.collibra.dgc.core.workflow.activiti.tasklistener.SetRoleResourceTaskListener">
            <activiti:field name="resourceId" expression="${resourceIdToOverride}" />
            <activiti:field name="resourceType" expression="${resourceTypeToOverride}"></activiti:field>
        </activiti:taskListener>
    </extensionElements>
</userTask>

API v2

<scriptTask id="scripttask1" name="scripttask1" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        execution.setVariableLocal("itemResourceIdCandidateOverride", ${resourceIdToOverride});
        execution.setVariableLocal("itemResourceTypeCandidateOverride", ${resourceTypeToOverride});
    ]]></script>
</scriptTask>

SetValueTaskListener

API v1

<userTask id="usertask1" name="usertask1" activiti:candidateUsers="role(Reviewer)">
<extensionElements>
    ...
    <activiti:taskListener event="create" class="com.collibra.dgc.core.workflow.activiti.tasklistener.SetValueTaskListener">
        <activiti:field name="resultVariable">
            <activiti:string>
		        <![CDATA[proposedUsers]]>
		    </activiti:string>
        </activiti:field>
        <activiti:field name="userExpression">
            <activiti:expression>
	            <![CDATA[${reviewerUserExpression}]]>
	        </activiti:expression>
        </activiti:field>
    </activiti:taskListener>
    ...
</extensionElements>
</userTask>

Add the following script as a step before 
usertask1
.

API v2

<scriptTask id="scripttask1" name="Set reviewer as proposed users" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        String userNames = users.getUserNamesCsv("${reviewerUserExpression}");
        execution.setVariableLocal("proposedUsers", userNames);
    ]]></script>
</scriptTask>

                Listeners
                            

                                Overview of task listeners
                

 

 

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

