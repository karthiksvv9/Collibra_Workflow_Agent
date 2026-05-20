// #importFile NONE
import com.collibra.client.api.AssetApi
import com.collibra.client.dto.Asset
import com.collibra.client.dto.AssetFilter

// Retrieve process variables
String domainIdStr = variables['domainId']
def domainId = string2Uuid(domainIdStr)

// Build filter for assets with status 'obsolete'
AssetFilter filter = new AssetFilter()
filter.setStatus('obsolete')

// Call Collibra API to get assets
AssetApi assetApi = new AssetApi()
List<Asset> obsoleteAssets = assetApi.getAssets(domainId, filter)

// Store list in process variable
variables['obsoleteAssets'] = obsoleteAssets
