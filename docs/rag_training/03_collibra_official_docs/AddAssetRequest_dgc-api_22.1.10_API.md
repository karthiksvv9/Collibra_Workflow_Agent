# AddAssetRequest (dgc-api 22.1.10 API)

Source: https://developer.collibra.com/apis/java/javav2/com/collibra/dgc/core/api/dto/instance/asset/AddAssetRequest.html



AddAssetRequest (dgc-api 22.1.10 API)

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
 
com.collibra.dgc.core.api.dto.instance.asset

Class AddAssetRequest

Object

AddAssetRequest

All Implemented Interfaces:

Serializable

public class 
AddAssetRequest

extends 
Object

implements 
Serializable

The properties of the asset to be added.

See Also:

Serialized Form

Nested Class Summary

Nested Classes

Modifier and Type

Class

Description

static class 

AddAssetRequest.Builder

 

Constructor Summary

Constructors

Constructor

Description

AddAssetRequest
()

 

Method Summary

All Methods
Static Methods
Instance Methods
Concrete Methods

Modifier and Type

Method

Description

static 
AddAssetRequest.Builder

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

 

String

getDisplayName
()

The display name of the new asset.

UUID

getDomainId
()

Required.
 The ID of the domain that the new asset should be added to.

Boolean

getExcludedFromAutoHyperlinking
()

Whether or not to exclude the new asset from auto hyperlinking.

UUID

getId
()

The ID of the new asset.

String

getName
()

Required.
 The full name of the new asset.

UUID

getStatusId
()

The ID of the status of the new asset.

UUID

getTypeId
()

The ID of the asset type of the new asset.

String

getTypePublicId
()

The public ID of the asset type of the new asset.

int

hashCode
()

 

void

setDisplayName
(
String
 displayName)

The display name of the new asset.

void

setDomainId
(
UUID
 domainId)

Required.
 The ID of the domain that the new asset should be added to.

void

setExcludedFromAutoHyperlinking
(
Boolean
 excludedFromAutoHyperlinking)

Whether or not to exclude the new asset from auto hyperlinking.

void

setId
(
UUID
 id)

The ID of the new asset.

void

setName
(
String
 name)

Required.
 The full name of the new asset.

void

setStatusId
(
UUID
 statusId)

The ID of the status of the new asset.

void

setTypeId
(
UUID
 typeId)

The ID of the asset type of the new asset.

void

setTypePublicId
(
String
 typePublicId)

The public ID of the asset type of the new asset.

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

AddAssetRequest

public
 
AddAssetRequest
()

Method Details

builder

public static
 
AddAssetRequest.Builder
 
builder
()

getName

public
 
String
 
getName
()

Required.
 The full name of the new asset. Should be unique within the domain.

getDisplayName

public
 
String
 
getDisplayName
()

The display name of the new asset.

getDomainId

public
 
UUID
 
getDomainId
()

Required.
 The ID of the domain that the new asset should be added to.

getTypeId

public
 
UUID
 
getTypeId
()

The ID of the asset type of the new asset.

getId

public
 
UUID
 
getId
()

The ID of the new asset.

getStatusId

public
 
UUID
 
getStatusId
()

The ID of the status of the new asset.

getExcludedFromAutoHyperlinking

public
 
Boolean
 
getExcludedFromAutoHyperlinking
()

Whether or not to exclude the new asset from auto hyperlinking.

getTypePublicId

public
 
String
 
getTypePublicId
()

The public ID of the asset type of the new asset.

setName

public
 
void
 
setName
(
String
 name)

Required.
 The full name of the new asset. Should be unique within the domain.

setDisplayName

public
 
void
 
setDisplayName
(
String
 displayName)

The display name of the new asset.

setDomainId

public
 
void
 
setDomainId
(
UUID
 domainId)

Required.
 The ID of the domain that the new asset should be added to.

setTypeId

public
 
void
 
setTypeId
(
UUID
 typeId)

The ID of the asset type of the new asset.

setId

public
 
void
 
setId
(
UUID
 id)

The ID of the new asset.

setStatusId

public
 
void
 
setStatusId
(
UUID
 statusId)

The ID of the status of the new asset.

setExcludedFromAutoHyperlinking

public
 
void
 
setExcludedFromAutoHyperlinking
(
Boolean
 excludedFromAutoHyperlinking)

Whether or not to exclude the new asset from auto hyperlinking.

setTypePublicId

public
 
void
 
setTypePublicId
(
String
 typePublicId)

The public ID of the asset type of the new asset.

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

