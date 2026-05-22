// #importFile NONE

String assetName = execution.getVariable("assetName") as String
String domainIdText = execution.getVariable("domainId") as String
String assetTypePublicId = execution.getVariable("assetTypePublicId") as String

if (!assetName?.trim()) {
    throw new IllegalArgumentException("assetName is required")
}
if (!domainIdText?.trim()) {
    throw new IllegalArgumentException("domainId is required")
}
if (!assetTypePublicId?.trim()) {
    throw new IllegalArgumentException("assetTypePublicId is required")
}

def domainId = string2Uuid(domainIdText.trim())
execution.setVariable("domainIdNormalized", domainId.toString())
execution.setVariable("assetNameNormalized", assetName.trim())
execution.setVariable("assetTypePublicIdNormalized", assetTypePublicId.trim())
