#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

jsons=${BASEDIR}/..

count=$1
half=$(expr ${count} / 2)

PORT=$2

for i in $(seq 1 ${count}); do
    curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction_withsender.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:${PORT}/mine_block
done

for i in $(seq 1 ${count}); do
    curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction_withsender.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:${PORT}/mine_block
done

curl -s GET http://127.0.0.1:${PORT}/is_valid | jq
sleep 5
curl -s GET http://127.0.0.1:${PORT}/get_chain | jq



