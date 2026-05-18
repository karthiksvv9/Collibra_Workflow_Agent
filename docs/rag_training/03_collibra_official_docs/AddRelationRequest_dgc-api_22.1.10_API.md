# AddRelationRequest (dgc-api 22.1.10 API)

Source: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/relation/AddRelationRequest.html



AddRelationRequest (dgc-api 22.1.10 API)

JavaScript is disabled on your browser.

 
 
 

Skip navigation links

Overview

Package

Class

Tree

Deprecated

Index

Help

Summary:

Nested

Field

Constr

Method

Detail:

Field

Constr

Method

Summary: 

Nested
 | 

Field | 

Constr
 | 

Method

Detail: 

Field | 

Constr
 | 

Method

SEARCH

Package
 
com.collibra.dgc.core.api.dto.instance.relation

Class AddRelationRequest

Object

AddRelationRequest

All Implemented Interfaces:

Serializable

public class 
AddRelationRequest

extends 
Object

implements 
Serializable

The properties of the relation to be added.

See Also:

Serialized Form

Nested Class Summary

Nested Classes

Modifier and Type

Class

Description

static class 

AddRelationRequest.Builder

 

Constructor Summary

Constructors

Constructor

Description

AddRelationRequest
()

 

Method Summary

All Methods
Static Methods
Instance Methods
Concrete Methods
Deprecated Methods

Modifier and Type

Method

Description

static 
AddRelationRequest.Builder

builder
()

 

protected boolean

canEqual
(
Object
 other)

 

boolean

equals
(
Object
 o)

 

Long

getEndingDate
()

Deprecated.

To be removed without replacement.

UUID

getSourceId
()

Required.
 The ID of the source of the relation.

Long

getStartingDate
()

Deprecated.

To be removed without replacement.

UUID

getTargetId
()

Required.
 The ID of the target of the relation.

UUID

getTypeId
()

The ID of the type of the relation.

String

getTypePublicId
()

The public ID of the type of the relation.

int

hashCode
()

 

void

setEndingDate
(
Long
 endingDate)

Deprecated.

To be removed without replacement.

void

setSourceId
(
UUID
 sourceId)

Required.
 The ID of the source of the relation.

void

setStartingDate
(
Long
 startingDate)

Deprecated.

To be removed without replacement.

void

setTargetId
(
UUID
 targetId)

Required.
 The ID of the target of the relation.

void

setTypeId
(
UUID
 typeId)

The ID of the type of the relation.

void

setTypePublicId
(
String
 typePublicId)

The public ID of the type of the relation.

String

toString
()

 

Methods inherited from class 
Object

clone
, 
finalize
, 
getClass
, 
notify
, 
notifyAll
, 
wait
, 
wait
, 
wait

Constructor Details

AddRelationRequest

public
 
AddRelationRequest
()

Method Details

builder

public static
 
AddRelationRequest.Builder
 
builder
()

getSourceId

public
 
UUID
 
getSourceId
()

Required.
 The ID of the source of the relation.

getTargetId

public
 
UUID
 
getTargetId
()

Required.
 The ID of the target of the relation.

getTypeId

public
 
UUID
 
getTypeId
()

The ID of the type of the relation.

getStartingDate

@Deprecated

public
 
Long
 
getStartingDate
()

Deprecated.

To be removed without replacement.

The starting date of the relation.

getEndingDate

@Deprecated

public
 
Long
 
getEndingDate
()

Deprecated.

To be removed without replacement.

The ending date of the relation.

getTypePublicId

public
 
String
 
getTypePublicId
()

The public ID of the type of the relation.

setSourceId

public
 
void
 
setSourceId
(
UUID
 sourceId)

Required.
 The ID of the source of the relation.

setTargetId

public
 
void
 
setTargetId
(
UUID
 targetId)

Required.
 The ID of the target of the relation.

setTypeId

public
 
void
 
setTypeId
(
UUID
 typeId)

The ID of the type of the relation.

setStartingDate

@Deprecated

public
 
void
 
setStartingDate
(
Long
 startingDate)

Deprecated.

To be removed without replacement.

The starting date of the relation.

setEndingDate

@Deprecated

public
 
void
 
setEndingDate
(
Long
 endingDate)

Deprecated.

To be removed without replacement.

The ending date of the relation.

setTypePublicId

public
 
void
 
setTypePublicId
(
String
 typePublicId)

The public ID of the type of the relation.

equals

public
 
boolean
 
equals
(
Object
 o)

Overrides:

equals
 in class 
Object

canEqual

protected
 
boolean
 
canEqual
(
Object
 other)

hashCode

public
 
int
 
hashCode
()

Overrides:

hashCode
 in class 
Object

toString

public
 
String
 
toString
()

Overrides:

toString
 in class 
Object

