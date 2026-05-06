#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Bringing down the network..."
./network.sh down

# Note: ./network.sh down safely handles all Fabric-specific cleanup.

echo "Bringing up the network and creating channel..."
./network.sh up createChannel -ca

echo "Pulling Fabric nodeenv image..."
docker pull hyperledger/fabric-nodeenv:2.5

echo "Deploying chaincode..."
./network.sh deployCC \
 -ccn v2v \
 -ccp ../chaincode/v2v/javascript \
 -ccl javascript \
 -ccv 1.0 \
 -ccep "OR('Org1MSP.peer','Org2MSP.peer')"

echo "✅ All steps completed successfully!"
