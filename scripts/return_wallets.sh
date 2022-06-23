#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

wallet_endpoint="http://127.0.0.1:6500/get_wallets"
cmd=($(curl -sS -X GET ${wallet_endpoint} | jq -r '.wallets[].blake2b'))

count=$1
for i in $(seq 1 ${count}); do
    if [[ ! -z ${cmd} ]]; then
        for i in $(echo ${cmd[@]}); do
            _r=$(echo $((RANDOM%200+100)).5)
            data='{"sender": "'"${i}"'","amount": '${_r}',"receiver": "'"${cmd[-1]}"'","message": "from mini blockchain tech script"}'
            curl -sX POST http://127.0.0.1:5005/add_transaction \
                -d "${data}" \
                -H "Content-Type: application/json"
        done
        curl -s http://127.0.0.1:5005/mint_block
        /usr/bin/python3 ${BASEDIR}/../core/data/sync-db.py 5005
    else
        echo "seems to be no wallets..."
    fi
done