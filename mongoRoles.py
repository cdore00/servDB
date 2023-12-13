

bdSystemList = ["", "admin", "local", "config"]

actionsList = [
{
	"resource" : {
			"db" : "config",
			"collection" : ""
	},
	"actions" : [
			"analyzeShardKey",
			"bypassDocumentValidation",
			"changeCustomData",
			"changePassword",
			"changeStream",
			"clearJumboFlag",
			"collMod",
			"collStats",
			"configureQueryAnalyzer",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createRole",
			"createSearchIndexes",
			"createUser",
			"dbHash",
			"dbStats",
			"dropCollection",
			"dropRole",
			"dropUser",
			"enableSharding",
			"find",
			"getDatabaseVersion",
			"getShardVersion",
			"grantRole",
			"indexStats",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"moveChunk",
			"planCacheRead",
			"refineCollectionShardKey",
			"remove",
			"reshardCollection",
			"revokeRole",
			"setAuthenticationRestriction",
			"splitChunk",
			"splitVector",
			"update",
			"viewRole",
			"viewUser"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.js"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : ""
	},
	"actions" : [
			"analyzeShardKey",
			"bypassDocumentValidation",
			"changeCustomData",
			"changePassword",
			"changeStream",
			"clearJumboFlag",
			"collMod",
			"collStats",
			"configureQueryAnalyzer",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createRole",
			"createSearchIndexes",
			"createUser",
			"dbHash",
			"dbStats",
			"dropCollection",
			"dropRole",
			"dropUser",
			"enableSharding",
			"find",
			"getDatabaseVersion",
			"getShardVersion",
			"grantRole",
			"indexStats",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"moveChunk",
			"planCacheRead",
			"refineCollectionShardKey",
			"remove",
			"reshardCollection",
			"revokeRole",
			"setAuthenticationRestriction",
			"splitChunk",
			"splitVector",
			"update",
			"viewRole",
			"viewUser"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.js"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : ""
	},
	"actions" : [
			"analyze",
			"analyzeShardKey",
			"bypassDocumentValidation",
			"changeCustomData",
			"changePassword",
			"changeStream",
			"clearJumboFlag",
			"collMod",
			"collStats",
			"compact",
			"compactStructuredEncryptionData",
			"configureQueryAnalyzer",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createRole",
			"createSearchIndexes",
			"createUser",
			"dbHash",
			"dbStats",
			"dropCollection",
			"dropDatabase",
			"dropIndex",
			"dropRole",
			"dropSearchIndex",
			"dropUser",
			"enableProfiler",
			"enableSharding",
			"find",
			"getDatabaseVersion",
			"getShardVersion",
			"grantRole",
			"indexStats",
			"insert",
			"killCursors",
			"listCachedAndActiveUsers",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"moveChunk",
			"planCacheIndexFilter",
			"planCacheRead",
			"planCacheWrite",
			"refineCollectionShardKey",
			"reIndex",
			"remove",
			"renameCollectionSameDB",
			"reshardCollection",
			"revokeRole",
			"setAuthenticationRestriction",
			"splitChunk",
			"splitVector",
			"storageDetails",
			"update",
			"validate",
			"viewRole",
			"viewUser"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.sessions"
	},
	"actions" : [
			"collStats",
			"dbStats",
			"getDatabaseVersion",
			"getShardVersion",
			"indexStats"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.replset"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "replset.election"
	},
	"actions" : [
			"bypassDocumentValidation",
			"collMod",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dropCollection",
			"find",
			"insert",
			"updateSearchIndex",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "replset.minvalid"
	},
	"actions" : [
			"bypassDocumentValidation",
			"collMod",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dropCollection",
			"find",
			"insert",
			"updateSearchIndex",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.profile"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"convertToCapped",
			"createCollection",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "local",
			"collection" : "system.healthlog"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"dbHash",
			"dbStats",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.users"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.roles"
	},
	"actions" : [
			"changeStream",
			"collStats",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.users"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead",
			"remove",
			"update"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.version"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "system.backup_users"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead"
	]
},
{
	"resource" : {
			"db" : "",
			"collection" : "system.js"
	},
	"actions" : [
			"bypassDocumentValidation",
			"changeStream",
			"collMod",
			"collStats",
			"compactStructuredEncryptionData",
			"convertToCapped",
			"createCollection",
			"createIndex",
			"createSearchIndexes",
			"dbHash",
			"dbStats",
			"dropCollection",
			"dropIndex",
			"dropSearchIndex",
			"find",
			"insert",
			"killCursors",
			"listCollections",
			"listIndexes",
			"listSearchIndexes",
			"updateSearchIndex",
			"planCacheRead",
			"remove",
			"renameCollectionSameDB",
			"update"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "settings"
	},
	"actions" : [
			"find",
			"insert",
			"update"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "tempusers"
	},
	"actions" : [
			"find"
	]
},
{
	"resource" : {
			"db" : "admin",
			"collection" : "temproles"
	},
	"actions" : [
			"find"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.preimages"
	},
	"actions" : [
			"find",
			"remove"
	]
},
{
	"resource" : {
			"db" : "config",
			"collection" : "system.change_collection"
	},
	"actions" : [
			"find",
			"insert",
			"remove",
			"update"
	]
}
]

systemRole = ['read','readWrite','dbAdmin','dbOwner','userAdmin','clusterAdmin','clusterManager','clusterMonitor','hostManager','backup','restore','readAnyDatabase','readWriteAnyDatabase','userAdminAnyDatabase','dbAdminAnyDatabase','dbOwner','userAdmin','userAdminAnyDatabase','root']


