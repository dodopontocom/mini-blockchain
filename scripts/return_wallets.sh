#!/usr/bin/env bash

BASEDIR="$(cd $(dirname ${BASH_SOURCE[0]}) >/dev/null 2>&1 && pwd)"

wallet_endpoint="http://127.0.0.1:6500/get_wallets"
curl -sS -X GET "http://127.0.0.1:6500/create_wallet" | jq -r 

count=$1
for i in $(seq 1 ${count}); do
    create_wallet=$(echo $((RANDOM % 5)))
    if [[ ${create_wallet} == 3 ]]; then
	curl -sS -X GET "http://127.0.0.1:6500/create_wallet" | jq -r 
    fi
    cmd=($(curl -sS -X GET ${wallet_endpoint} | jq -r '.wallets[].blake2b'))
    if [[ ! -z ${cmd} ]]; then
        for i in $(echo ${cmd[@]}); do
            _amount=$(echo $((RANDOM%200+100)).5)
	    _receiver=$(echo $((RANDOM % ${#cmd[@]})))
            data='{"sender": "'"${i}"'","amount": '${_amount}',"receiver": "'"${cmd[_receiver]}"'","message": "from mini blockchain tech script"}'
            curl -sSX POST http://127.0.0.1:5005/add_transaction \
                -d "${data}" \
                -H "Content-Type: application/json"
        done
        curl -sS http://127.0.0.1:5005/mint_block
        #/usr/bin/python3 ${BASEDIR}/../core/data/sync-db.py 5005
    else
        echo "seems to be no wallets..."
    fi
done
