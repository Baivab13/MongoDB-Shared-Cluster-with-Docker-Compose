Demo Mongo Sharded Cluster with Docker Compose
=========================================

### WARNING
> It is only Tested on Linux (Ubuntu 20.04)
---

### Mongo Components (Architecture)

* Config Server (3 member replica set): `configsvr01`,`configsvr02`,`configsvr03`
* 3 Shards (each a 3 member `PSS` replica set):
	* `shard01-a`,`shard01-b`, `shard01-c`
	* `shard02-a`,`shard02-b`, `shard02-c`
	* `shard03-a`,`shard03-b`, `shard03-c`
* 2 Routers (mongos): `router01`, `router02`

<img src="https://raw.githubusercontent.com/kuwar/cbbn/master/images/sharding-and-replica-sets-architecture.png" style="width: 100%;" />

### Setup
- **Step 1: Start all of the containers**

```bash
docker-compose up -d
```

- **Step 2: Initialize the replica sets (config servers and shards)**

```bash
docker-compose exec configsvr01 sh -c "mongo < /scripts/init-configserver.js"

docker-compose exec shard01-a sh -c "mongo < /scripts/init-shard01.js"
docker-compose exec shard02-a sh -c "mongo < /scripts/init-shard02.js"
docker-compose exec shard03-a sh -c "mongo < /scripts/init-shard03.js"
```

- **Step 3: Initializing the router**
>Note: Wait a bit for the config server and shards to elect their primaries before initializing the router

```bash
docker-compose exec router01 sh -c "mongo < /scripts/init-router.js"
```

- **Step 4: Enable sharding and setup sharding-key**
```bash
docker-compose exec router01 mongo --port 27017

// Enable sharding for database `cbbn`
sh.enableSharding("cbbn")

// Setup shardingKey for collection `users`**
db.adminCommand( { shardCollection: "cbbn.users", key: { email: "hashed" } } )

```

> Done! but before you start inserting data you should verify them first

### Verify

- **Verify the status of the sharded cluster**

```bash
docker-compose exec router01 mongo --port 27017
sh.status()
```
*Sample Result:*
```
  mongos> sh.status()
--- Sharding Status --- 
  sharding version: {
        "_id" : 1,
        "minCompatibleVersion" : 5,
        "currentVersion" : 6,
        "clusterId" : ObjectId("5f096a9c588316a0c474afa6")
  }
  shards:
        {  "_id" : "rs-shard-01",  "host" : "rs-shard-01/shard01-a:27017,shard01-b:27017,shard01-c:27017",  "state" : 1 }
        {  "_id" : "rs-shard-02",  "host" : "rs-shard-02/shard02-a:27017,shard02-b:27017,shard02-c:27017",  "state" : 1 }
        {  "_id" : "rs-shard-03",  "host" : "rs-shard-03/shard03-a:27017,shard03-b:27017,shard03-c:27017",  "state" : 1 }
  active mongoses:
        "4.2.8" : 2
  autosplit:
        Currently enabled: yes
  balancer:
        Currently enabled:  yes
        Currently running:  yes
        Failed balancer rounds in last 5 attempts:  0
        Migration Results for the last 24 hours: 
                268 : Success
  databases:
        {  "_id" : "cbbn",  "primary" : "rs-shard-02",  "partitioned" : true,  "version" : {  "uuid" : UUID("b8b5dfd3-840a-42d0-8fe8-82fe3faf3643"),  "lastMod" : 1 } }
                cbbn.users
                        shard key: { "email" : "hashed" }
                        unique: false
                        balancing: true
                        chunks:
                                rs-shard-01     2
                                rs-shard-02     2
                                rs-shard-03     2
                        { "email" : { "$minKey" : 1 } } -->> { "email" : NumberLong("-6148914691236517204") } on : rs-shard-01 Timestamp(1, 0) 
                        { "email" : NumberLong("-6148914691236517204") } -->> { "email" : NumberLong("-3074457345618258602") } on : rs-shard-01 Timestamp(1, 1) 
                        { "email" : NumberLong("-3074457345618258602") } -->> { "email" : NumberLong(0) } on : rs-shard-02 Timestamp(1, 2) 
                        { "email" : NumberLong(0) } -->> { "email" : NumberLong("3074457345618258602") } on : rs-shard-02 Timestamp(1, 3) 
                        { "email" : NumberLong("3074457345618258602") } -->> { "email" : NumberLong("6148914691236517204") } on : rs-shard-03 Timestamp(1, 4) 
                        { "email" : NumberLong("6148914691236517204") } -->> { "email" : { "$maxKey" : 1 } } on : rs-shard-03 Timestamp(1, 5) 
        {  "_id" : "cbnn",  "primary" : "rs-shard-02",  "partitioned" : true,  "version" : {  "uuid" : UUID("04dc80ec-7ab4-4400-8da8-e8b7adaf15d1"),  "lastMod" : 1 } }
        {  "_id" : "config",  "primary" : "config",  "partitioned" : true }
                config.system.sessions
                        shard key: { "_id" : 1 }
                        unique: false
                        balancing: true
                        chunks:
                                rs-shard-01     756
                                rs-shard-02     134
                                rs-shard-03     134
                        too many chunks to print, use verbose if you want to force print

```

- **Verify status of replica set for each shard**
> You should see 1 PRIMARY, 2 SECONDARY

```bash
docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.status()' | mongo --port 27017" 
docker exec -it cbbn-shard-02-node-a bash -c "echo 'rs.status()' | mongo --port 27017" 
docker exec -it cbbn-shard-03-node-a bash -c "echo 'rs.status()' | mongo --port 27017" 
```
*Sample Result:*
```
kuwar@kuwar-Inspiron-5570:~/Documents/EPITA/MongoDB/cbbn$ docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.status()' | mongo --port 27017" 
MongoDB shell version v4.2.8
connecting to: mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb
Implicit session: session { "id" : UUID("0e0ecda5-39ef-479f-87b3-c91b7a235fcd") }
MongoDB server version: 4.2.8
{
        "set" : "rs-shard-01",
        "date" : ISODate("2020-07-11T08:47:37.717Z"),
        "myState" : 1,
        "term" : NumberLong(1),
        "syncingTo" : "",
        "syncSourceHost" : "",
        "syncSourceId" : -1,
        "heartbeatIntervalMillis" : NumberLong(2000),
        "majorityVoteCount" : 2,
        "writeMajorityCount" : 2,
        "optimes" : {
                "lastCommittedOpTime" : {
                        "ts" : Timestamp(1594457257, 1),
                        "t" : NumberLong(1)
                },
                "lastCommittedWallTime" : ISODate("2020-07-11T08:47:37.134Z"),
                "readConcernMajorityOpTime" : {
                        "ts" : Timestamp(1594457257, 1),
                        "t" : NumberLong(1)
                },
                "readConcernMajorityWallTime" : ISODate("2020-07-11T08:47:37.134Z"),
                "appliedOpTime" : {
                        "ts" : Timestamp(1594457257, 7),
                        "t" : NumberLong(1)
                },
                "durableOpTime" : {
                        "ts" : Timestamp(1594457257, 7),
                        "t" : NumberLong(1)
                },
                "lastAppliedWallTime" : ISODate("2020-07-11T08:47:37.138Z"),
                "lastDurableWallTime" : ISODate("2020-07-11T08:47:37.138Z")
        },
        "lastStableRecoveryTimestamp" : Timestamp(1594457229, 3),
        "lastStableCheckpointTimestamp" : Timestamp(1594457229, 3),
        "electionCandidateMetrics" : {
                "lastElectionReason" : "electionTimeout",
                "lastElectionDate" : ISODate("2020-07-11T08:03:57.560Z"),
                "electionTerm" : NumberLong(1),
                "lastCommittedOpTimeAtElection" : {
                        "ts" : Timestamp(0, 0),
                        "t" : NumberLong(-1)
                },
                "lastSeenOpTimeAtElection" : {
                        "ts" : Timestamp(1594454626, 1),
                        "t" : NumberLong(-1)
                },
                "numVotesNeeded" : 2,
                "priorityAtElection" : 1,
                "electionTimeoutMillis" : NumberLong(10000),
                "numCatchUpOps" : NumberLong(0),
                "newTermStartDate" : ISODate("2020-07-11T08:03:59.134Z"),
                "wMajorityWriteAvailabilityDate" : ISODate("2020-07-11T08:04:01.856Z")
        },
        "members" : [
                {
                        "_id" : 0,
                        "name" : "shard01-a:27017",
                        "health" : 1,
                        "state" : 1,
                        "stateStr" : "PRIMARY",
                        "uptime" : 5028,
                        "optime" : {
                                "ts" : Timestamp(1594457257, 7),
                                "t" : NumberLong(1)
                        },
                        "optimeDate" : ISODate("2020-07-11T08:47:37Z"),
                        "syncingTo" : "",
                        "syncSourceHost" : "",
                        "syncSourceId" : -1,
                        "infoMessage" : "",
                        "electionTime" : Timestamp(1594454637, 1),
                        "electionDate" : ISODate("2020-07-11T08:03:57Z"),
                        "configVersion" : 1,
                        "self" : true,
                        "lastHeartbeatMessage" : ""
                },
                {
                        "_id" : 1,
                        "name" : "shard01-b:27017",
                        "health" : 1,
                        "state" : 2,
                        "stateStr" : "SECONDARY",
                        "uptime" : 2631,
                        "optime" : {
                                "ts" : Timestamp(1594457256, 4),
                                "t" : NumberLong(1)
                        },
                        "optimeDurable" : {
                                "ts" : Timestamp(1594457256, 3),
                                "t" : NumberLong(1)
                        },
                        "optimeDate" : ISODate("2020-07-11T08:47:36Z"),
                        "optimeDurableDate" : ISODate("2020-07-11T08:47:36Z"),
                        "lastHeartbeat" : ISODate("2020-07-11T08:47:36.971Z"),
                        "lastHeartbeatRecv" : ISODate("2020-07-11T08:47:36.971Z"),
                        "pingMs" : NumberLong(0),
                        "lastHeartbeatMessage" : "",
                        "syncingTo" : "shard01-a:27017",
                        "syncSourceHost" : "shard01-a:27017",
                        "syncSourceId" : 0,
                        "infoMessage" : "",
                        "configVersion" : 1
                },
                {
                        "_id" : 2,
                        "name" : "shard01-c:27017",
                        "health" : 1,
                        "state" : 2,
                        "stateStr" : "SECONDARY",
                        "uptime" : 2631,
                        "optime" : {
                                "ts" : Timestamp(1594457256, 6),
                                "t" : NumberLong(1)
                        },
                        "optimeDurable" : {
                                "ts" : Timestamp(1594457256, 4),
                                "t" : NumberLong(1)
                        },
                        "optimeDate" : ISODate("2020-07-11T08:47:36Z"),
                        "optimeDurableDate" : ISODate("2020-07-11T08:47:36Z"),
                        "lastHeartbeat" : ISODate("2020-07-11T08:47:37.091Z"),
                        "lastHeartbeatRecv" : ISODate("2020-07-11T08:47:37.532Z"),
                        "pingMs" : NumberLong(0),
                        "lastHeartbeatMessage" : "",
                        "syncingTo" : "shard01-b:27017",
                        "syncSourceHost" : "shard01-b:27017",
                        "syncSourceId" : 1,
                        "infoMessage" : "",
                        "configVersion" : 1
                }
        ],
        "ok" : 1,
        "$gleStats" : {
                "lastOpTime" : Timestamp(0, 0),
                "electionId" : ObjectId("7fffffff0000000000000001")
        },
        "lastCommittedOpTime" : Timestamp(1594457257, 1),
        "$configServerState" : {
                "opTime" : {
                        "ts" : Timestamp(1594457257, 8),
                        "t" : NumberLong(1)
                }
        },
        "$clusterTime" : {
                "clusterTime" : Timestamp(1594457257, 14),
                "signature" : {
                        "hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
                        "keyId" : NumberLong(0)
                }
        },
        "operationTime" : Timestamp(1594457257, 7)
}
bye

```

- **Check database status**
```bash
docker-compose exec router01 mongo --port 27017
use cbbn
db.stats()
db.users.getShardDistribution()
```

*Sample Result:*
```
mongos> db.users.getShardDistribution()

Shard rs-shard-03 at rs-shard-03/shard03-a:27017,shard03-b:27017,shard03-c:27017
 data : 0B docs : 0 chunks : 2
 estimated data per chunk : 0B
 estimated docs per chunk : 0

Shard rs-shard-02 at rs-shard-02/shard02-a:27017,shard02-b:27017,shard02-c:27017
 data : 0B docs : 0 chunks : 2
 estimated data per chunk : 0B
 estimated docs per chunk : 0

Shard rs-shard-01 at rs-shard-01/shard01-a:27017,shard01-b:27017,shard01-c:27017
 data : 0B docs : 0 chunks : 2
 estimated data per chunk : 0B
 estimated docs per chunk : 0

Totals
 data : 0B docs : 0 chunks : 6
 Shard rs-shard-03 contains 0% data, 0% docs in cluster, avg obj size on shard : 0B
 Shard rs-shard-02 contains 0% data, 0% docs in cluster, avg obj size on shard : 0B
 Shard rs-shard-01 contains 0% data, 0% docs in cluster, avg obj size on shard : 0B

```

### More commands

```bash
docker exec -it cbbn-mongo-config-01 bash -c "echo 'rs.status()' | mongo --port 27017"


docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.help()' | mongo --port 27017"
docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.status()' | mongo --port 27017" 
docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.printReplicationInfo()' | mongo --port 27017" 
docker exec -it cbbn-shard-01-node-a bash -c "echo 'rs.printSlaveReplicationInfo()' | mongo --port 27017"
```

---

### Normal Startup
The cluster only has to be initialized on the first run. Subsequent startup can be achieved simply with `docker-compose up` or `docker-compose up -d`

### Resetting the Cluster
To remove all data and re-initialize the cluster, make sure the containers are stopped and then:

```bash
docker-compose rm
```

### Clean up docker-compose
```bash
docker-compose down -v --rmi all --remove-orphans
```

Execute the **First Run** instructions again.

### Screenshot

<img src="https://raw.githubusercontent.com/kuwar/cbbn/master/images/containers.png" style="width: 100%;" />
<img src="https://raw.githubusercontent.com/kuwar/cbbn/master/images/enable-shard-db-n-collection.png" style="width: 100%;" />
<img src="https://raw.githubusercontent.com/kuwar/cbbn/master/images/shard-status.png" style="width: 100%;" />
<img src="https://raw.githubusercontent.com/kuwar/cbbn/master/images/data-sharding-n-replication.png" style="width: 100%;" />

