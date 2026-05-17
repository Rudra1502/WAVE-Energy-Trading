#!/bin/bash

# ==============================
# MASTER EXPERIMENT RUNNER
# Runs baseline + proposed with clean state
# ==============================

set -e

NUM_TX=${1:-500}

echo "============================================"
echo "  V2V Adaptive Consensus - Full Experiment"
echo "  Transactions per mode: $NUM_TX"
echo "============================================"

# ==============================
# STEP 1: Source environment
# ==============================
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
export ORDERER_CA=${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

echo ""
echo "[1/6] Registering EVs..."
for i in {1..6}; do
    peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    --waitForEvent \
    -C mychannel -n v2v \
    -c "{\"function\":\"registerEV\",\"Args\":[\"EV$i\"]}" \
    > /dev/null 2>&1 || true
    echo "  Registered EV$i"
done

echo ""
echo "[2/6] Registering 50 Validators..."
for i in {1..50}; do
    peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    --waitForEvent \
    -C mychannel -n v2v \
    -c "{\"function\":\"registerValidator\",\"Args\":[\"V$i\",\"100\"]}" \
    > /dev/null 2>&1 || true
    echo "  Registered V$i"
done

echo ""
echo "============================================"
echo "[3/6] Running BASELINE experiment ($NUM_TX tx)..."
echo "============================================"
BASELINE_START=$(date +%s)
cd scripts
bash run_experiment.sh baseline $NUM_TX
cd ..
BASELINE_END=$(date +%s)
BASELINE_TIME=$((BASELINE_END - BASELINE_START))
echo "Baseline done in ${BASELINE_TIME}s"

echo "Finalizing last block for baseline..."
peer chaincode invoke -o localhost:7050 \
--ordererTLSHostnameOverride orderer.example.com \
--tls --cafile "$ORDERER_CA" \
--waitForEvent \
-C mychannel -n v2v \
-c '{"function":"finalizeCurrentBlock","Args":[]}' \
> /dev/null 2>&1 || true

echo ""
echo "[4/6] Resetting all validators for clean proposed run..."
peer chaincode invoke -o localhost:7050 \
--ordererTLSHostnameOverride orderer.example.com \
--tls --cafile "$ORDERER_CA" \
--waitForEvent \
-C mychannel -n v2v \
-c '{"function":"resetAllValidators","Args":[]}' \
2>&1 | tail -1
echo "  Validators reset!"

echo ""
echo "============================================"
echo "[5/6] Running PROPOSED experiment ($NUM_TX tx)..."
echo "============================================"
PROPOSED_START=$(date +%s)
cd scripts
bash run_experiment.sh proposed $NUM_TX
cd ..
PROPOSED_END=$(date +%s)
PROPOSED_TIME=$((PROPOSED_END - PROPOSED_START))
echo "Proposed done in ${PROPOSED_TIME}s"

echo "Finalizing last block for proposed..."
peer chaincode invoke -o localhost:7050 \
--ordererTLSHostnameOverride orderer.example.com \
--tls --cafile "$ORDERER_CA" \
--waitForEvent \
-C mychannel -n v2v \
-c '{"function":"finalizeCurrentBlock","Args":[]}' \
> /dev/null 2>&1 || true

echo ""
echo "[6/6] Running analysis..."
cd results
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi
python3 analyze.py
cd ..

echo ""
echo "============================================"
echo "  ALL DONE!"
echo "  Baseline: ${BASELINE_TIME}s"
echo "  Proposed: ${PROPOSED_TIME}s"
echo "  Results in: test-network/results/"
echo "============================================"

echo ""
echo "Opening log files..."
start results/baseline_log.txt 2>/dev/null || xdg-open results/baseline_log.txt 2>/dev/null &
start results/proposed_log.txt 2>/dev/null || xdg-open results/proposed_log.txt 2>/dev/null &
