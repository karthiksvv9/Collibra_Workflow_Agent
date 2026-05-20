// #importFile NONE
import com.collibra.sdk.api.AssetApi
import com.collibra.sdk.dto.Asset

// Retrieve asset UUID from process variable
String assetUuidStr = assetId
def assetUuid = string2Uuid(assetUuidStr)

// Delete asset
AssetApi.deleteAsset(assetUuid)
