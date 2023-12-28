import json
import requests

posts = []

def analystic_chain(node_address):
    """
    Hàm get chain từ node, phân tíc dữ liệu và lưu trữ cục bộ
    """
    global posts
    get_chain_address = "{}/chain".format(node_address)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)
        posts = sorted(content,
                       key=lambda k: k['timestamp'],
                       reverse=True)
        

def norm_host(node_address):
    if node_address[-1] != '/':
        node_address += '/'
    return node_address