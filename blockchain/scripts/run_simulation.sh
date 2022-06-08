#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

jsons=${BASEDIR}/..

count=$1
half=$(expr ${count} / 2)

id=$1
telegram_token=$2

PORTS=($3)

FLASK_ENV=development ./miniapi.py 6003

for i in $(echo ${PORTS[@]}); do
    curl -sSs http://127.0.0.1:${i}/replace_chain >/dev/null 2>&1
    message=$(echo "node port: ${i} has $(curl -s http://127.0.0.1:${i}/get_chain | jq '.length') block(s) in the chain")
    echo ${message}
    curl -X POST -H 'Content-Type: application/json' \
        -d "{\"chat_id\": ${id}, \"text\": \"${message}\", \"disable_notification\": true}" \
        https://api.telegram.org/bot${telegram_token}/sendMessage
done

exit 0
curl -s http://127.0.0.1:${i}/replace_chain | jq


for i in $(seq 1 ${count}); do
    for t in $(ls ${jsons}/_transaction*.json); do
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
    
    curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction_withsender.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:${PORT}/mint_block
    
    curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction_withsender.json -H "Content-Type: application/json"
    for i in $(seq 1 ${half}); do
        curl -sX POST http://127.0.0.1:${PORT}/add_transaction -d @${jsons}/transaction.json -H "Content-Type: application/json"
    done
    curl -s GET http://127.0.0.1:${PORT}/mint_block
    
done

sleep 2
curl -s GET http://127.0.0.1:${PORT}/is_valid | jq
sleep 2
curl -s GET http://127.0.0.1:${PORT}/get_chain | jq