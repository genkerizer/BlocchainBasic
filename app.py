import json
import time
import requests
from flask import Flask, request
from core.block import Block
from core.utils import norm_host
from core.blockchain import Blockchain



 
app =  Flask(__name__)
blockchain = Blockchain()
PEERS = set()

def consensus_process():
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in PEERS:
        response = requests.post('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True
    return False


def synchronized_chain(lasted_blockchain):
    global blockchain
    try:
        for peer in PEERS:
            requests.post("{}add_block".format(peer), 
                         data=json.dumps({'latest_chain': lasted_blockchain.chain}),
                         headers = {'Content-Type': "application/json"})
    except:
        return "Cannot update blockchain\n", 401
    return "Update successful\n", 200
        


def added_block_to_all_peer(block):
    for peer in PEERS:
        print(">>>>>>>>>>>>:\t", peer)
        url = "{}add_block".format(peer)
        requests.post(url, 
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers = {'Content-Type': "application/json"})
        

@app.route('/update_chain', methods=['POST'])
def update_chain_in_network():
    global blockchain
    lasted_chain = request.get_json()['latest_chain']
    blockchain.update_chain = lasted_chain
    return True


@app.route('/chain', methods=['POST'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(PEERS)})


@app.route('/get_pending_transactions', methods=['POST'])
def get_pending_transactions():
    return json.dumps(blockchain.unconfirmed_transactions)


# route thêm một peer mới vào mạng
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # Địa chỉ host đến các node ngang hàng 
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Node address is not valid\n", 400
    PEERS.add(node_address)
    PEERS.add(request.host_url)
    return get_chain()

@app.route('/save_chain', methods=['POST'])
def save_chain():
    chain_file_name = request.form["filename"]
    if chain_file_name is not None:
        with open(chain_file_name, 'w') as chain_file:
            chain_file.write(get_chain())


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Trong nội bộ gọi đến route `register_node` để
    đăng ký node hiện tại với node từ xa được chỉ định trong
    request và cập nhật lại mạng blockchain
    """
    node_address = request.form["node_address"]

    if not node_address:
        return "\nNode address is not valid", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    node_address = norm_host(node_address)

    # Request đăng ký với node từ xa và lấy thông tin
    response = requests.post(node_address + "register_node",
                             data=json.dumps(data), headers=headers)
    

    if response.status_code == 200:
        global blockchain
        global PEERS

        # update chain và các peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        PEERS.update(set(response.json()['peers']))
        PEERS.add(node_address)
        return "Registration successful\n", 200
    else:
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        merkle_root = block_data['merkle_root']
        generated_blockchain.add_block(block, proof, merkle_root)
    return generated_blockchain


@app.route('/add_block', methods=['POST'])
def check_valid_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])
    added_flag = blockchain.add_block(block, block_data['hash'], block_data['merkle_root'])

    if not added_flag:
        return "The block cannot add in node\n", 400
    return "Block added to the chain\n", 201
 

@app.route('/mine_transaction', methods=['POST'])
def mine_transactions():
    # synchronized_chain(blockchain)
    result = blockchain.mining_block()
    if not result:
        return "No transactions to mine\n", 400
    else:
        chain_length = len(blockchain.chain)
        consensus_process()
        if chain_length == len(blockchain.chain):
            added_block_to_all_peer(blockchain.last_block)
        blockchain.unconfirmed_transactions = []
        return "Block {} is mined.\n".format(blockchain.last_block.index), 200


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()['data']
    if data is None:
        return "Invlaid transaction data\n", 404
    blockchain.add_transaction(data)
    return "Sucessfully\n", 200


@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.form["data"]
    target_node = request.form["target_node"]
    target_node = norm_host(target_node)
    if data is None:
        return 'Data is not valid', 400
    data_json = {
        'data': data
    }

    if target_node != request.host_url:
        PEERS.add(target_node)
        
    transaction_address = "{}new_transaction".format(target_node)
    response = requests.post(transaction_address,
                            json=data_json,
                            headers={'Content-type': 'application/json'})
    return response.content, response.status_code
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)