from helper import *
from flask import Flask,request
import json

if True:
	app = Flask(__name__)
	chain=BlockChain()
	chain.peers=set()
	peers=chain.peers

	chain.mine()

	@app.route('/transactions',methods=['POST'])
	def add_transactions():
		results=request.get_json()
		print(results)
		if not results:
			return "None",400           #not for demostration
		chain.unchain.append(results)
		return 'ok'


	@app.route('/chain',methods=['GET'])
	def return_chain():
		chain_data = []
		for block in chain.chain: 
			chain_data.append(block.__dict__)
		return json.dumps([{'len':chain.length,'chain':chain_data}])

	@app.route('/add_peers',methods=['POST'])
	def add_peers():
		node=request.get_json()
		if not node:
			return "none",400
		peers.append(node['url'])

	@app.route('/mine',methods=['GET'])
	def mine():
		chain.mine()
		return 'ok'

	@app.route('/add_block',methods=['POST'])
	def add_block():
		block_data = request.get_json()
		block = Block(block_data["index"], block_data["transactions"],
			block_data["timestamp"], block_data['note'],block_data["previous_hash"],block_data['proof'])
		if chain.add2Chain(block):
			return 'success'
		else:
			return 'fail'

	def consensus():            #this is wrong 
		global chain

		len=chain.length
		for i in peers:
			response=requests.get('http://{}/chain'.format(node))
			len1=response.json()['len']
			if len1>len:
				chain.len=len1
				chain.chain=response.json()['chain']

	app.run(debug=True)
