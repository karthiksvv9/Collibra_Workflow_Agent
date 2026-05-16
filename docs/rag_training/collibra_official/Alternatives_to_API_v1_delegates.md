# Alternatives to API v1 delegates

Source: https://developer.collibra.com/workflows/workflow-documentation/Content/Workflows/ExecutionLogic/ref_deprecated-delegates.htm

 

Alternatives to API v1 delegates

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
 

 
Service task
 

 
Delegates
 
 

                Delegates
                            

                                GetRelations and RemoveRelations delegates
                

 

 

 Alternatives to API v1 delegates

This section provides examples of alternatives to Java Core API v1 delegates.

AddAttributeDelegate

API v1

<serviceTask id="servicetask1" name="Add attribute" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.attribute.AddAttributeDelegate">
    <extensionElements>
        <activiti:field name="value">
            <activiti:string><![CDATA[attribute content]]></activiti:string>
        </activiti:field>
        <activiti:field name="ownerId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="typeId">
            <activiti:expression><![CDATA[${givenAttributeTypeId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Add attribute" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest;
        def attribute = attributeApi.addAttribute(AddAttributeRequest.builder()
            .assetId(item.id)
            .typeId(string2Uuid(givenAttributeTypeId)))
            .value("attribute content")
            .build())
        execution.setVariable("output", attribute)
    ]]></script>
</scriptTask>

GetAttributeDelegate

API v1

<serviceTask id="servicetask1" name="Get attribute" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.attribute.GetAttributeDelegate">
    <extensionElements>
        <activiti:field name="attributeId">
            <activiti:expression><![CDATA[${givenAttributeId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Get attribute" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        def attribute = attributeApi.getAttribute(string2Uuid(givenAttributeId));
        execution.setVariable("output", attribute)
    ]]></script>
</scriptTask>

RemoveAttributeDelegate

API v1

<serviceTask id="servicetask1" name="Remove attribute" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.attribute.RemoveAttributeDelegate">
    <extensionElements>
        <activiti:field name="attributeId">
            <activiti:expression><![CDATA[${givenAttributeId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Remove attribute" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        attributeApi.removeAttribute(string2Uuid(givenAttributeId));
    ]]></script>
</scriptTask>

AddRelationDelegate

API v1

<serviceTask id="servicetask1" name="Add relation" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.relation.GetRelationsDelegate">
    <extensionElements>
        <activiti:field name="sourceTermId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="targetTermId">
            <activiti:expression><![CDATA[${givenTargetResourceId}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="binaryFactTypeId">
            <activiti:expression><![CDATA[${givenRelationTypeId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Add relation" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest;
        def relation = relationApi.addRelation(AddRelationRequest.builder()
            .typeId(string2Uuid(givenRelationTypeId))
            .sourceId(item.id)
            .targetId(givenTargetResourceId)
            .build());
        execution.setVariable("output", relation)
    ]]></script>
</scriptTask>

GetRelationsDelegate

API v1

<serviceTask id="servicetask1" name="Remove relation" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.relation.GetRelationsDelegate">
    <extensionElements>
        <activiti:field name="sourceTermId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Remove relation" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;        
        def relations = relationApi.findRelations(FindRelationsRequest.builder()
            .sourceId(item.id)
            .build())
        .getResults();
        execution.setVariable("output", relations)
    ]]></script>
</scriptTask>

RemoveRelationsDelegate

API v1

<serviceTask id="servicetask1" name="Remove relation" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.relation.RemoveRelationsDelegate">
    <extensionElements>
        <activiti:field name="sourceTermId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Remove relation" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;        
        def relations = relationApi.findRelations(FindRelationsRequest.builder()
            .sourceId(item.id)
            .build())
        .getResults();
        relationApi.removeRelations(new ArrayList(relations.collect{ it.getId() }));
    ]]></script>
</scriptTask>

AddResourceRoleDelegate

API v1

<serviceTask id="servicetask1" name="Assign owner" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.roles.AddResourceRoleDelegate">
    <extensionElements>
        <activiti:field name="resourceId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="userName">
            <activiti:expression><![CDATA[${startUser}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="roleId">
            <activiti:expression><![CDATA[${roleId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Assign owner" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.responsibility.AddResponsibilityRequest
        def userName = execution.getVariable("startUser")
        def ownerUserId = userApi.getUserByUsername(userName).getId();           
        responsibilityApi.addResponsibility(AddResponsibilityRequest.builder()
            .resourceId(item.id)
            .resourceType(item.type)
            .roleId(string2Uuid(roleId))
            .ownerId(ownerUserId)
            .build())
    ]]></script>
</scriptTask>

RemoveResourceRoleDelegate

API v1

<serviceTask id="servicetask1" name="Remove current Owner role" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.roles.RemoveResourceRoleDelegate">
    <extensionElements>
        <activiti:field name="roleName">
            <activiti:string><![CDATA[Owner]]></activiti:string>
        </activiti:field>
        <activiti:field name="userName">
            <activiti:expression><![CDATA[${ownerName}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="resourceId">
            <activiti:expression><![CDATA[${domain.id}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Remove current Owner role" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.responsibility.FindResponsibilitiesRequest
        def ownerUserId = userApi.getUserByUsername(ownerName).getId();
        def ownerRoleId = users.getRoleId("Owner");
        def responsibilities = responsibilityApi.findResponsibilities(FindResponsibilitiesRequest.builder()
            .resourceIds(Collections.singletonList(domain.id))
            .ownerIds(Collections.singletonList(ownerUserId))
            .roleIds(Collections.singletonList(ownerRoleId))
            .build())
         .getResults()
        responsibilityApi.removeResponsibilities(new ArrayList(responsibilities.collect{ it.getId() }));
    ]]></script>
</scriptTask>

AddTermDelegate

API v1

<serviceTask id="servicetask1" name="Add term" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.term.AddTermDelegate">
    <extensionElements>
        <activiti:field name="signifier">
            <activiti:expression>${givenSignifier}</activiti:expression>
        </activiti:field>
        <activiti:field name="vocabularyId">
            <activiti:expression>${givenVocabularyId}</activiti:expression>
        </activiti:field>
        <activiti:field name="typeId">
            <activiti:expression>${givenTypeId}</activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Add asset" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest;
        import com.collibra.dgc.core.api.model.instance.Asset;
        Asset asset = assetApi.addAsset(AddAssetRequest.builder()
            .name(givenSignifier)
            .displayName(givenSignifier)
            .typeId(string2Uuid(givenTypeId))
            .domainId(string2Uuid(givenVocabularyId))
            .build())
        execution.setVariable("output", asset)
    ]]></script>
</scriptTask>

GetTermDelegate

API v1

<serviceTask id="servicetask1" name="Get term" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.term.GetTermDelegate">
    <extensionElements>
        <activiti:field name="termId">
            <activiti:expression><![CDATA[${giventTermId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Get asset" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.model.instance.Asset;
        Asset asset = assetApi.getAsset(givenAssetId);
        execution.setVariable("output", asset)
    ]]></script>
</scriptTask>

RemoveTermDelegate

API v1

<serviceTask id="servicetask1" name="Remove term" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.term.RemoveTermDelegate">
    <extensionElements>
        <activiti:field name="termId">
            <activiti:expression><![CDATA[${givenTermId}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Remove asset" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        assetApi.removeAsset(givenAssetId);
    ]]></script>
</scriptTask>

AddComment

API v1

<serviceTask id="servicetask1" name="Add comment" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.AddComment">
    <extensionElements>
        <activiti:field name="comment">
            <activiti:string>The content of the comment.</activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Store comment" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.comment.AddCommentRequest
        commentApi.addComment(AddCommentRequest.builder()
            .content("The content of the comment.")
            .baseResourceId(item.getId())
            .baseResourceType(item.getType())
            .build())
    ]]></script>
</scriptTask>

AddDecisionVote

API v1

<serviceTask id="servicetask1" name="Add vote outcome to list" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.AddDecisionVote"></serviceTask>

API v2

<scriptTask id="scripttask1" name="Add vote outcome to list" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        def voter = execution.getVariable("voter");
        Boolean approved = (Boolean) execution.getVariable("approve");
        comment = execution.getVariable("comment");
        vote = [
            "name" : voter,
            "approved": approved,
            "comment": comment?.toString()
        ]
        voting = execution.getVariable("votingResult");
        voting.add(vote);
        checkEarlyComplete(execution, voting);
        execution.setVariable("votingResult", voting);
        def checkEarlyComplete(execution, voting) {
            Boolean earlyComplete = (Boolean) execution.getVariable("earlyComplete");
            if (earlyComplete) {
                Long percentage = (Long) execution.getVariable("votePercentage");
                List<String> voters = (List<String>) execution.getVariable("voters");
                double approved = 0;
                double disapproved = 0;
                double totalVoters = voters.size();
                for (Map vote : voting) {
                    if (vote.approved) {
                        approved++;
                    }
                    else {
                        disapproved++;
                    }
                }
                if (approved / totalVoters >= percentage / 100.0) {
                    execution.setVariable("completion", Boolean.TRUE);
                }
                else if (disapproved / totalVoters > (100 - percentage) / 100.0) {
                    execution.setVariable("completion", Boolean.TRUE);
                }
            }
        }
    ]]></script>
</scriptTask>

ChangeIssueResponsibleCommunity

API v1

<serviceTask id="servicetask1" name="Move the Issue" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.ChangeIssueResponsibleCommunity">
    <extensionElements>
        <activiti:field name="responsibleCommunity">
            <activiti:expression>${responsibleCommunity}</activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Move the Issue" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script>
        import com.collibra.dgc.core.api.dto.instance.issue.MoveIssueRequest
        issueApi.moveIssue(MoveIssueRequest.builder()
            .issueId(item.id)
            .communityId(responsibleCommunity)
            .build())
    </script>
</scriptTask>

ChangeStatusDelegate

API v1

<serviceTask id="servicetask1" name="Mark as Accepted" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.ChangeStatusDelegate"
    <extensionElements>
        <activiti:field name="targetStatusId">
            <activiti:string><![CDATA[00000000-0000-0000-0000-000000005009]]></activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Mark as Accepted" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest
        String acceptedStatusId = "00000000-0000-0000-0000-000000005009"
        assetApi.changeAsset(ChangeAssetRequest.builder()
            .id(item.id)
            .statusId(string2Uuid(acceptedStatusId))
            .build())
    ]]></script>
</scriptTask>

StateChanger

API v1

<serviceTask id="servicetask1" name="Mark as Accepted" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.StateChanger"
    <extensionElements>
        <activiti:field name="targetStatusId">
            <activiti:string><![CDATA[00000000-0000-0000-0000-000000005009]]></activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Mark as Accepted" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.asset.ChangeAssetRequest
        String acceptedStatusId = "00000000-0000-0000-0000-000000005009"
        assetApi.changeAsset(ChangeAssetRequest.builder()
            .id(item.id)
            .statusId(string2Uuid(acceptedStatusId))
            .build())
    ]]></script>
</scriptTask>

CountVoteResult

API v1

<serviceTask id="servicetask1" name="Count voting result" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.CountVoteResult"></serviceTask>

API v2

<scriptTask id="scripttask1" name="Count voting result" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        def voting = execution.getVariable("votingResult")
        boolean result = getResult(voting, execution)
        execution.setVariable("votingSuccess", result)
        def getResult(voting, execution) {
            Long percentage = (Long) execution.getVariable("votePercentage");
            if (!voting.isEmpty()) {
                int requiredToVote = ((List<String>) execution.getVariable("voters")).size();
                int approved = getNumberOfApprovals(voting);
                double fraction = percentage / 100.0;
                return approved >= requiredToVote * fraction;
            }
            return false;
        }
        def getNumberOfApprovals(List<Map> voting) {
            int approved = 0;
            for (Map vote : voting) {
                    if (vote.approved) {
                        approved++;
                    }
                }
            return approved;
        }
    ]]></script>
</scriptTask>

CreateIssue

API v1

<serviceTask id="servicetask1" name="Create issue" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.CreateIssue">
    <extensionElements>
        <activiti:field name="subject">
            <activiti:expression>${subject}</activiti:expression>
        </activiti:field>
        <activiti:field name="description">
            <activiti:expression>${description}</activiti:expression>
        </activiti:field>
        <activiti:field name="priority">
            <activiti:expression>${priority}</activiti:expression>
        </activiti:field>
        <activiti:field name="relations">
            <activiti:expression>${relations}</activiti:expression>
        </activiti:field>
        <activiti:field name="classifications">
            <activiti:expression>${classifications}</activiti:expression>
        </activiti:field>
        <activiti:field name="requester">
            <activiti:expression>${requester}</activiti:expression>
        </activiti:field>
        <activiti:field name="responsibleCommunity">
            <activiti:expression>${responsibleCommunity}</activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Create issue" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.issue.RelatedAssetReference;
        import com.collibra.dgc.core.api.dto.instance.issue.AddIssueRequest;
        import com.collibra.dgc.core.api.dto.user.FindUsersRequest;
        def requesterId = userApi.getUserByUsername(requester).getId()
        def descriptionString = execution.getVariable("description")?.toString() ?: ""
        def communityId = responsibleCommunity
        def relatedAssets = execution.getVariable("relatedAssets") ?: []
        def relatedAssetsList = []
        relatedAssets.each{
            relatedAssetId ->
            def relatedAssetRef = RelatedAssetReference.builder()
                .assetId(relatedAssetId)
                .direction(true)
                .relationTypeId(string2Uuid(impactsRelationId))
                .build()
            relatedAssetsList.add(relatedAssetRef)
        }
        def newIssueUuid = issueApi.addIssue(AddIssueRequest.builder()
            .name(subject)
            .description(descriptionString)
            .priority(priority)
            .responsibleCommunityId(communityId)
            .relatedAssets(relatedAssetsList)
            .categoryIds(classifications)
            .typeId(string2Uuid(dataIssueId))
            .requesterId(requesterId)
            .build())
        .getId()
        execution.setVariable("outputCreatedTermId", newIssueUuid))
    ]]></script>
</scriptTask>

CreateVotersList

API v1

<serviceTask id="servicetask1" name="Create list of voters" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.CreateVotersList">
    <extensionElements>
        <activiti:field name="voterUserExpression">
            <activiti:expression><![CDATA[${voterUserExpression}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Create list of voters" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        def voterUserExpression = execution.getVariable("voterUserExpression")
        final Set<String> voters = new HashSet<>();
        for (String userExpression : utility.toList(voterUserExpression)) {
            voters.addAll(users.getUserNamesWithError(userExpression));
        }
        execution.setVariable("voters", new ArrayList<>(voters));
        execution.setVariable("votingResult", []);
        execution.setVariable("completion", Boolean.FALSE);
    ]]></script>
</scriptTask>

GetModel

API v1

<serviceTask id="servicetask1" name="Get Model" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.GetModel">
    <extensionElements>
        <activiti:field name="viewConfig">
            <activiti:expression>${viewConfig}</activiti:expression>
        </activiti:field>
        <activiti:field name="varNames">
            <activiti:string>VOC_ID</activiti:string>
        </activiti:field>
        <activiti:field name="varValues">
            <activiti:expression>${item.id}</activiti:expression>
        </activiti:field>
        <activiti:field name="resultVariable">
            <activiti:string>assets</activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

This delegate is not supported and there is no alternative or possibility to use it.

GetRelatedTerms

API v1

<serviceTask id="servicetask1" name="Get related terms" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.GetRelatedTerms">
    <extensionElements>
        <activiti:field name="relationRole">
            <activiti:expression>"role(Business Steward)"</activiti:expression>
        </activiti:field>
        <activiti:field name="resultVariable">
            <activiti:string>relations</activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Get related terms" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.model.meta.type.RelationType;
        import com.collibra.dgc.core.api.dto.meta.relationtype.FindRelationTypesRequest;
        import com.collibra.dgc.core.api.model.instance.Relation;
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;
        import com.collibra.dgc.core.api.model.reference.NamedResourceReference;
        import com.collibra.dgc.workflow.api.exception.WorkflowException;
        List<RelationType> relationTypes = relationTypeApi.findRelationTypes(FindRelationTypesRequest.builder()
            .role("groups")
            .build())
        .getResults()
        if (relationTypes.isEmpty()) {
            throw new WorkflowException("No relation types for provided role 'groups'");
        }
        List<UUID> relatedAssetIds = new ArrayList<>();
        for (RelationType relationType : relationTypes) {
            List<Relation> relations = relationApi.findRelations(FindRelationsRequest.builder()
                .sourceId(item.id)
                .relationTypeId(relationType.getId())
                .build())
            .getResults();
            for (Relation relation : relations) {
                relatedAssetIds.add(relation.getTarget().getId());
            }
        }
        execution.setVariable("relations", relatedAssetIds);
    ]]></script>
</scriptTask>

GetRelatedTermsDelegate

API v1

<serviceTask id="servicetask1" name="Get related terms" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.GetRelatedTermsDelegate">
    <extensionElements>
        <activiti:field name="termId">
            <activiti:expression><![CDATA[${item.id}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="direction">
            <activiti:string>true</activiti:string>
        </activiti:field>
        <activiti:field name="relationTypeId">
            <activiti:string>"00000000-0000-0000-0000-000000007021"</activiti:string>
        </activiti:field>
        <activiti:field name="resultVariableName">
            <activiti:string>"relatedAssets"</activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Get related terms" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.model.instance.Asset;
        import com.collibra.dgc.core.api.model.instance.Relation;
        import com.collibra.dgc.core.api.dto.instance.relation.FindRelationsRequest;
        assetId = item.id;
        direction = Boolean.TRUE;
        groupsRelationTypeId = string2Uuid("00000000-0000-0000-0000-000000007021");
        List<Asset> relatedAssets = new ArrayList<>();
        if (direction) {
            List<Relation> relations = relationApi.findRelations(FindRelationsRequest.builder()
                .sourceId(assetId)
                .relationTypeId(groupsRelationTypeId)
                .build())
            .getResults();
            for (Relation relation : relations) {
                relatedAssets.add(relation.getSource());
            }
        }
		else {
            List<Relation> relations = relationApi.findRelations(FindRelationsRequest.builder()
                .targetId(assetId)
                .relationTypeId(groupsRelationTypeId)
                .build())
            .getResults();
            for (Relation relation : relations) {
                relatedAssets.add(relation.getTarget());
            }
        }
        execution.setVariable("relatedAssets", relatedAssets);
    ]]></script>
</scriptTask>

GetUserNames

API v1

<serviceTask id="servicetask1" name="Get user names" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.GetUserNames">
    <extensionElements>
        <activiti:field name="userNames">
            <activiti:expression><![CDATA[${userName}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="userExpressions">
            <activiti:expression><![CDATA[${role}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="groupNames">
            <activiti:expression><![CDATA[${group}]]></activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Get user names" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.model.user.User;
        import com.collibra.dgc.core.api.model.usergroup.UserGroup;
        import com.collibra.dgc.core.api.dto.usergroup.FindUserGroupsRequest;
        Set<String> userNameResult = new HashSet<String>();
        userNameResult.addAll(utility.toList("${userName}"));
        userNameResult.addAll(users.getUserNames("${role}"));
        List<UserGroup> userGroupList = userGroupApi.findUserGroups(FindUserGroupsRequest.builder()
            .name("${group}")
            .nameMatchMode(MatchMode.EXACT)
            .build())
        .getResults()
        for (UserGroup userGroup : userGroupList) {
            List<User> userList = userApi.findUsers(FindUsersRequest.builder()
                .groupId(userGroup.getId())
                .build())
            .getResults()
            for (User user : userList) {
                userNameResult.add(user.getUserName());
            }
        }
        execution.setVariable("assembledUserNames", userNameResult);
    ]]></script>
</scriptTask>

MailSender

API v1

com.collibra.dgc.core.workflow.activiti.delegate.MailSender

API v2

com.collibra.dgc.workflow.api.listener.ActionMailSender

ProvideDefaultsDelegate

API v1

<serviceTask id="servicetask1" name="Check optional variables" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.ProvideDefaultsDelegate">
    <extensionElements>
        <activiti:field name="names">
            <activiti:string><![CDATA[resultTemplate,reminderTemplate]]></activiti:string>
        </activiti:field>
        <activiti:field name="defaults">
            <activiti:string><![CDATA[result,reminder]]></activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Check Optional Variables" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.workflow.api.exception.WorkflowException
        List<String> namesList = utility.toList(execution.getVariable("names"))
        List<String> defaultsList = utility.toList(execution.getVariable("defaults"))
        if(namesList.size() != defaultsList.size()) {
            loggerApi.error("names list contains " + namesList.size() + " elements while the default values list contains " +
defaultsList.size() + " elements. Those sizes should be equal.")
            String errorMessage = translation.getMessage("workflowNamesAndDefaultsSizeDontMatch",namesList.size(),defaultsList.size())
            String errorTitle = translation.getMessage("workflowValueNotAllowed");
            WorkflowException workflowException = new WorkflowException(errorMessage);
            ex.setTitleMessage(errorTitle);
            throw workflowException;
        }
        for (int i = 0; i < namesList.size(); i++) {
            String currentName = namesList.get(i).trim();
            String currentDefault = defaultsList.get(i);
            if (!execution.hasVariable(currentName)) {
                execution.setVariable(currentName, currentDefault);
            }
        }
    ]]></script>
</scriptTask>

StartCollibraConnectFlowDelegate

API v1

com.collibra.dgc.core.workflow.activiti.delegate.StartCollibraConnectFlowDelegate

API v2

com.collibra.dgc.workflow.api.delegate.StartCollibraConnectFlowDelegate

StartWorkflowInstanceDelegate

API v1

<serviceTask id="servicetask1" name="Start workflow" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.StartWorkflowInstanceDelegate">
    <extensionElements>
        <activiti:field name="processId">
            <activiti:string><![CDATA[subWorkflow]]></activiti:string>
        </activiti:field>
        <activiti:field name="resourceId">
            <activiti:expression><![CDATA[${targetTermId}]]></activiti:expression>
        </activiti:field>
        <activiti:field name="resourceType">
            <activiti:string><![CDATA[TE]]></activiti:string>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Start workflow" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.workflow.StartWorkflowInstancesRequest;
        import com.collibra.dgc.core.api.model.workflow.WorkflowBusinessItemType;
        def workflowDefinitionId = workflowDefinitionApi.getWorkflowDefinitionByProcessId(subWorkflow).getId();
        workflowInstanceApi.startWorkflowInstances(StartWorkflowInstancesRequest.builder()
            .workflowDefinitionId(workflowDefinitionId)
            .addBusinessItemId(string2Uuid(${targetTermId}))
            .businessItemType(WorkflowBusinessItemType.valueOf("ASSET"))
            .build())
    ]]></script>
</scriptTask>

TermIntakeDelegate

API v1

<serviceTask id="servicetask1" name="Create Term" activiti:class="com.collibra.dgc.core.workflow.activiti.delegate.TermIntakeDelegate">
    <extensionElements>
        <activiti:field name="signifier">
            <activiti:expression>${signifier}</activiti:expression>
        </activiti:field>
        <activiti:field name="conceptType">
            <activiti:expression>${conceptType}</activiti:expression>
        </activiti:field>
        <activiti:field name="vocabulary">
            <activiti:expression>${intakeVocabulary}</activiti:expression>
        </activiti:field>
        <activiti:field name="definition">
            <activiti:expression>${definition}</activiti:expression>
        </activiti:field>
        <activiti:field name="description">
            <activiti:expression>${description}</activiti:expression>
        </activiti:field>
        <activiti:field name="example">
            <activiti:expression>${example}</activiti:expression>
        </activiti:field>
        <activiti:field name="usesrelation">
            <activiti:expression>${usesrelation}</activiti:expression>
        </activiti:field>
        <activiti:field name="note">
            <activiti:expression>${note}</activiti:expression>
        </activiti:field>
    </extensionElements>
</serviceTask>

API v2

<scriptTask id="scripttask1" name="Create Asset" scriptFormat="groovy" activiti:autoStoreVariables="false">
    <script><![CDATA[
        import com.collibra.dgc.core.api.dto.instance.asset.AddAssetRequest;
        import com.collibra.dgc.core.api.dto.instance.attribute.AddAttributeRequest;
        import com.collibra.dgc.core.api.dto.instance.relation.AddRelationRequest;
        def note = execution.getVariable("note")
        def definition = execution.getVariable("definition")  
        def newAssetUuid = assetApi.addAsset(AddAssetRequest.builder()
            .name(signifier)
            .displayName(signifier)
            .typeId(conceptType)
            .domainId(string2Uuid(intakeVocabulary))
            .build())
        .getId()
        addAttributeToAsset(newAssetUuid,definition,definitionAttributeTypeUuid)
        addAttributeToAsset(newAssetUuid,note,noteAttributeTypeUuid)
        addRelationsWithOneSourceAndMultipleTargetsToAsset(newAssetUuid,usesRelationTypeUuid,usesrelation)
        execution.setVariable("outputCreatedTermId",uuid2String(newAssetUuid))
        def addAttributeToAsset(assetUuid,attributeValue,attributeTypeUuid) {
            if (attributeValue == null){
                return;
            }
            attributeApi.addAttribute(AddAttributeRequest.builder()
                .assetId(assetUuid)
                .typeId(string2Uuid(attributeTypeUuid))
                .value(attributeValue.toString())
                .build())
        } 
        def addRelationsWithOneSourceAndMultipleTargetsToAsset(sourceUuid,relationTypeUuid,targetUuidList) {
            def addRelationsRequests = []
            loggerApi.info("Source: " + sourceUuid.toString())
            loggerApi.info("Type: " + relationTypeUuid.toString())
            loggerApi.info("Target: " + targetUuidList.toString())
            loggerApi.info("Target Class" + targetUuidList.getClass().toString())
            targetUuidList.each{ t ->
            loggerApi.info("T Class" + t.getClass().toString())
            addRelationsRequests.add(AddRelationRequest.builder()
                .sourceId(sourceUuid)
                .targetId(t)
                .typeId(string2Uuid(relationTypeUuid))
                .build())
            }
            relationApi.addRelations(addRelationsRequests)
        }
    ]]></script>
</scriptTask>

                Delegates
                            

                                GetRelations and RemoveRelations delegates
                

 

 

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

