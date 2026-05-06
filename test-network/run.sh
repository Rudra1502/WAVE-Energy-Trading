#!/bin/bash

set -e

echo "🚀 Registering EVs..."

for i in {1..70}
do
peer chaincode invoke -o localhost:7050 \
--ordererTLSHostnameOverride orderer.example.com \
--tls --cafile "$ORDERER_CA" \
--waitForEvent \
-C mychannel -n v2v \
-c "{\"function\":\"registerEV\",\"Args\":[\"EV$i\"]}"
done

echo "🚀 Registering Validators..."

for i in {1..50}
do
peer chaincode invoke -o localhost:7050 \
--ordererTLSHostnameOverride orderer.example.com \
--tls --cafile "$ORDERER_CA" \
--waitForEvent \
-C mychannel -n v2v \
-c '{"function":"registerValidator","Args":[\"V$i\",\"100\"]}'
done

echo "Done!"
