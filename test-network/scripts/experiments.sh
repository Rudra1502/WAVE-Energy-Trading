#!/bin/bash

OUTPUT_FILE="../results/experiment_log.txt"
> $OUTPUT_FILE

echo "Running experiment..." >> $OUTPUT_FILE

NUM_TX=2000



for ((i=1; i<=NUM_TX; i++))
do
    START=$(date +%s%3N)
    BUYER="EV$(( (RANDOM % 3) + 1 ))"
    SELLER="EV$(( (RANDOM % 3) + 3 ))"

    RESULT=$(peer chaincode invoke -o localhost:7050 \
    --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    --waitForEvent \
    -C mychannel -n v2v \
    -c "{\"function\":\"completeTransaction\",\"Args\":[\"$BUYER\",\"$SELLER\",\"true\",\"0.3\"]}" \
    2>&1)

    echo $RESULT

    END=$(date +%s%3N)

    LATENCY=$((END - START))

    PAYLOAD=$(echo "$RESULT" | sed -n 's/.*payload:"\(.*\)".*/\1/p')
    
    CLEAN=$(echo "$PAYLOAD" | sed 's/\\"/"/g')
    
    VALIDATOR=$(echo "$CLEAN" | sed -n 's/.*validatorUsed":"\([^"]*\)".*/\1/p')
    
    echo "Tx $i | Validator: $VALIDATOR | Latency(ms): $LATENCY" >> $OUTPUT_FILE
done

echo "Done!"
