#!/bin/bash

# ==============================
# USAGE: ./run_experiment.sh <baseline|proposed> [num_tx]
# ==============================

MODE=${1:-"proposed"}
NUM_TX=${2:-500}

RESULTS_DIR="../results"
OUTPUT_FILE="${RESULTS_DIR}/${MODE}_log.txt"

mkdir -p "$RESULTS_DIR"
> "$OUTPUT_FILE"

echo "Running experiment: MODE=$MODE | NUM_TX=$NUM_TX" | tee -a "$OUTPUT_FILE"

for ((i=1; i<=NUM_TX; i++))
do
    START=$(date +%s%3N)

    # Random buyer (EV1-EV3) and seller (EV4-EV6)
    BUYER="EV$(( (RANDOM % 3) + 1 ))"
    SELLER="EV$(( (RANDOM % 3) + 4 ))"

    # ==============================
    # VARIABLE SUCCESS RATE (~80% true, ~20% false)
    # ==============================
    RAND_SUCCESS=$(( RANDOM % 100 ))
    if [ $RAND_SUCCESS -lt 80 ]; then
        SUCCESS="true"
    else
        SUCCESS="false"
    fi

    # ==============================
    # VARIABLE LATENCY (0.05 to 0.95)
    # ==============================
    LATENCY_INT=$(( RANDOM % 91 + 5 ))
    if [ $LATENCY_INT -lt 10 ]; then
        SIM_LATENCY="0.0${LATENCY_INT}"
    else
        SIM_LATENCY="0.${LATENCY_INT}"
    fi

    RESULT=$(peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    --waitForEvent \
    -C mychannel -n v2v \
    -c "{\"function\":\"completeTransaction\",\"Args\":[\"$BUYER\",\"$SELLER\",\"$SUCCESS\",\"$SIM_LATENCY\",\"$MODE\"]}" \
    2>&1)

    END=$(date +%s%3N)
    LATENCY=$((END - START))

    PAYLOAD=$(echo "$RESULT" | sed -n 's/.*payload:"\(.*\)".*/\1/p')
    CLEAN=$(echo "$PAYLOAD" | sed 's/\\"/"/g')
    VALIDATOR=$(echo "$CLEAN" | sed -n 's/.*validatorUsed":"\([^"]*\)".*/\1/p')

    echo "Tx $i | Validator: $VALIDATOR | Latency(ms): $LATENCY" | tee -a "$OUTPUT_FILE"
done

echo "Experiment $MODE completed! Results: $OUTPUT_FILE"
