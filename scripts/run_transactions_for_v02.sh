#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

jsons=${BASEDIR}/../testing

count=$1
half=$(expr ${count} / 2)

PORT=$2

for i in $(seq 1 ${count}); do
    for t in $(ls ${jsons}/_transactions*.json); do
        echo ${t}
        json_count=$(jq length ${t})
        echo ${json_count}
        _counter=0
        while [[ ${_counter} -lt ${json_count} ]]; do
            curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d "$(cat ${t} | jq ".[${_counter}]")" -H "Content-Type: application/json"
            cat ${t} | jq ".[${_counter}]"
            echo "- - - count: ${_counter}"
            _counter=$((_counter+1))
            #sleep 5
        done
        curl -s GET http://127.0.0.1:${PORT}/mint_block
    done
done