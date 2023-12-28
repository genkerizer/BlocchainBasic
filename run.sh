# # flask run --port 8000 &
# # flask run --port 8001 &
# # flask run --port 8002

# Khởi tạo peer2peer network
curl --request POST 'http://127.0.0.1:8000/register_with' --form 'node_address="http://127.0.0.1:8001"'
echo "\n"
curl --request POST 'http://127.0.0.1:8000/register_with' --form 'node_address="http://127.0.0.1:8002"'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/register_with' --form 'node_address="http://127.0.0.1:8002"'
echo "\n"

# # Kiểm tra chain trước khi giao dịch
curl --request POST 'http://127.0.0.1:8000/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8002/chain'
echo "\n"


# Tạo transaction
curl --request POST 'http://127.0.0.1:8001/send_data' --form 'data="1"' --form 'target_node="http://127.0.0.1:8000"'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/send_data' --form 'data="2"' --form 'target_node="http://127.0.0.1:8000"'
echo "\n"


# # Kiểm tra pending transaction
curl --request POST 'http://127.0.0.1:8000/get_pending_transactions'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/get_pending_transactions'
echo "\n"
curl --request POST 'http://127.0.0.1:8002/get_pending_transactions'
echo "\n"

## Tiến hành mining
curl --request POST 'http://127.0.0.1:8000/mine_transaction'

# Kiểm tra chain sau khi giao dịch
curl --request POST 'http://127.0.0.1:8000/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8002/chain'
echo "\n"


# Tạo transaction
curl --request POST 'http://127.0.0.1:8000/send_data' --form 'data="3"' --form 'target_node="http://127.0.0.1:8002"'
echo "\n"
curl --request POST 'http://127.0.0.1:8000/send_data' --form 'data="4"' --form 'target_node="http://127.0.0.1:8002"'
echo "\n"

## Tiến hành mining
curl --request POST 'http://127.0.0.1:8002/mine_transaction'

# Kiểm tra chain sau khi giao dịch
curl --request POST 'http://127.0.0.1:8000/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8001/chain'
echo "\n"
curl --request POST 'http://127.0.0.1:8002/chain'
echo "\n"
