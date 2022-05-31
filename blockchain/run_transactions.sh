#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

count=$1
half=$(expr ${count} / 2)

for i in $(seq 1 ${count}); do
    curl -sX POST http://127.0.0.1:5000/add_transaction -d @./transaction.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:5000/add_transaction -d @./transaction_withsender.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:5000/mine_block
done

for i in $(seq 1 ${count}); do
    curl -sX POST http://127.0.0.1:5000/add_transaction -d @./transaction_withsender.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:5000/add_transaction -d @./transaction.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:5000/mine_block
done

curl -s GET http://127.0.0.1:5000/is_valid | jq
sleep 5
curl -s GET http://127.0.0.1:5000/get_chain | jq



