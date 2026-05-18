# Adjusting for Groovy JavaBeans specification compatibility changes

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/DesignWorkflows/co_adjusting-for-groovy-javabeans-compatibility.htm

 

Adjusting for Groovy JavaBeans specification compatibility changes

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
 

 
Upgrading your scripts for Groovy 3 compatibility
 
 

                Change Groovy switch statement
                            

                                Bulk operations in Groovy script tasks
                

 

 

Adjusting for Groovy JavaBeans specification compatibility changes

Groovy 3 is more compliant with the JavaBeans specification for one edge case scenario involving any field having a name starting with an uppercase letter. This change has an impact on the handling of properties.

Groovy properties

The definition of properties according to the 
Groovy public documentation
 is:

A property is an externally visible feature of a class. Rather than just using a public field to represent such features (which provides a more limited abstraction and would restrict refactoring possibilities), the typical approach in Java is to follow the conventions outlined in the JavaBeans Specification, i.e. represent the property using a combination of a private backing field and getters/setters. Groovy follows these same conventions but provides a simpler way to define the property.

The code sample below will generate the following:

A backing 
private String name
 field, a 
getName
 and a 
setName
 method.

A backing 
private int age
 field, a 
getAge
 and a 
setAge
 method.

class Person {
    String name                             
    int age                                 
}

By convention, Groovy also recognizes properties even if there is no backing field, provided there are getters or setters that follow the Java Beans specification.
class PseudoProperties {
    //1. a pseudo property "name"
    void setName(String name) {}
    String getName() {}

    //2. a pseudo read-only property "age"
    int getAge() { 42 }

    //3. a pseudo write-only property "groovy"
    void setGroovy(boolean groovy) {  }
}
def p = new PseudoProperties()
p.name = 'Foo' // uses (1)                     
assert p.age == 42 // uses (2)                 
p.groovy = true // uses (3)

Groovy 3 breaking change

In Groovy 3 the handling of properties that start with an uppercase letter has changed to be more compliant with the JavaBeans specification.

The way how properties are mapped to the accessor method has changed. In groovy 2 it was possible to access the field instead of the accessor methods  in some scenarios as shown below:

Groovy 2
class A {
  private String X = 'fieldX'
  private String Prop = 'fieldProp'
  String getProp() { 'Prop' }
  String getX() { 'X' }
}
new A().with {
  assert prop == 'Prop' // uses getProp() accessor
  assert Prop == 'fieldProp' // uses field directly
  assert x == 'X' // uses getX() accessor
  assert X == 'fieldX' // uses field direclty
}

Groovy 3
class A {
  private String X = 'fieldX'
  private String Prop = 'fieldProp'
  String getProp() { 'Prop' }
  String getX() { 'X' }
}
new A().with {
  assert prop == 'Prop' // use getProp() accessor
  assert Prop == 'Prop' // use getProp() accessor
  assert x == 'X' // uses getX() accessor
  assert X == 'X' // uses getX() accessor
}

A similar situation occurs when you use static properties:

Groovy 2
class A {
  private static String X = 'fieldX'
  private static String Prop = 'fieldProp'
  static String getProp() { 'Prop' }
  static String getX() { 'X' }
}
A.with {
  assert prop == 'Prop' // uses static getProp() accessor
  assert Prop == 'fieldProp' // uses field directly
  assert x == 'X' // uses static getX() accessor
  assert X == 'fieldX' // uses field directly
}

Groovy 3
class A {
  private static String X = 'fieldX'
  private static String Prop = 'fieldProp'
  static String getProp() { 'Prop' }
  static String getX() { 'X' }
}
A.with {
  assert prop == 'Prop' // uses static getProp() accessor
  assert Prop == 'Prop' // uses static getProp() accessoor
  assert x == 'X' // uses static getX() accessor
  assert X == 'X' // uses static getX() accessor
}

This breaking change doesn’t affect classes where accessor methods are not overwritten.

Recommendation

To make existing workflow scripts compatible with Groovy 3, we recommend using lowercase property names, except in when the property name is all uppercase:
class A {
  private String X = 'fieldX'
  private String XML = 'fieldXML'
  
  String getX() { 'X' }
  String getXML() { 'XML' }
}
new A().with {
  assert x == 'X' // instead of using uppercase X property 
  assert XML == 'XML' // in this case using XML property is the only way
}

                Change Groovy switch statement
                            

                                Bulk operations in Groovy script tasks
                

 

 

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

