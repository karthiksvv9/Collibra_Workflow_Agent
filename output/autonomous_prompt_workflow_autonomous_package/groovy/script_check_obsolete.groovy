// #importFile NONE
import com.collibra.sdk.api.AssetApi
import com.collibra.sdk.dto.Asset
import com.collibra.sdk.api.RelationApi
import com.collibra.sdk.dto.Relation

// Retrieve asset UUID from process variable
String assetUuidStr = assetId
def assetUuid = string2Uuid(assetUuidStr)

// Check asset status
Asset asset = AssetApi.getAsset(assetUuid)
if (asset.status.toLowerCase() == 'obsolete') {
    return true
} else {
    return false
}
