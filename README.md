# mini-blockchain
A blockchain in python for study purpose

dependencies  
`$ pip3 install -r requirements.txt`  
`$ sudo apt-get install jq curl`  
(also install python3xxx)

run blockchain (if you change port number here, dont forget to also change in `nodes.json` file for the localhost server, default is `5000`)  
`$ cd mini-blockchain/blockchain`  
`$ PORT=5000 ./miniapi.py ${PORT}`

then sending several requests to the blockchain (in another terminal window)  
`$ PORT=5000 curl -s http://127.0.0.1:${PORT}/mint_block | jq`  
`$ PORT=5000 curl -s http://127.0.0.1:${PORT}/get_chain | jq`  
`$ PORT=5000 curl -s http://127.0.0.1:${PORT}/is_valid | jq`
