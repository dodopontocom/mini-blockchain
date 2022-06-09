#add to your local ~/.bashrc
export PYTHONPATH="<path_to_cloned_repository>/mini-blockchain/blockchain/"
export DB_USERNAME="<mongo_db_username>"
export DB_PASSWORD="<mongo_db_password>"
export MONGO_CLUSTER="<mongo_cluster>"
export MONGO_CONN_STRING="mongodb+srv://${DB_USERNAME}:${DB_PASSWORD}@${MONGO_CLUSTER}.zxn61de.mongodb.net/?retryWrites=true&w=majority"