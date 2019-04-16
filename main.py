from helper import *
from flask import Flask,request
import json
from flask import *

money=dict()

pair=dict()

database=[]

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
		result=chain.chain[-1].hash[6]
		for i in database:
			if i[0]==result:
				money[i[1]]+=int(i[2])
			else:
				money[i[1]]-=int(i[2])
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

	@app.route('/server.html')
	def login():
		response=make_response(render_template('server.html'))
		return response

	@app.route('/create')
	def create_Account():
		(public_key,private_key)=create_account()
		tmp=dict()
		pair[private_key.save_pkcs1()]=public_key.save_pkcs1()
		money[private_key.save_pkcs1()]=1000
		tmp['public_key']=public_key.save_pkcs1()
		tmp['private_key']=b64encode(private_key.save_pkcs1())
		result=json.dumps(tmp)
		return result

	@app.route('/xxx',methods=['GET','POST'])
	def xxx():
		if request.method=='GET':
			if request.cookies.get("1"):
				return render_template('admin.html')
			else:
				return "access denied"
		else:
			password=request.form.get('passwd')
			if password=='8888':
				resp=make_response(render_template('admin.html'))
				resp.set_cookie("1","1")
				return resp

	@app.route('/client',methods=['GET','POST'])
	def client():
		if request.cookies.get("key"):
			return redirect("/index", code=302, Response=None)
		return render_template("client.html")

	@app.route('/index',methods=['GET','POST'])
	def mainpage():
		if request.method == "GET":
			if request.cookies.get("key"):
				private_key=b64decode(request.cookies.get("key"))
				return render_template("main.html",balance=str(money[private_key]))
			return "please log in"
		else:
			private_key=b64decode(request.form['passwd'])
			print(money)
			balance=money[private_key]
			print(balance)
			resp=make_response(render_template("main.html",balance=str(money[private_key])))
			resp.set_cookie("key",b64encode(private_key))
			return resp


	@app.route('/pay',methods=['POST'])
	def pay_tmp():
		if request.cookies.get("key"):
			private_key=b64decode(request.cookies.get("key"))
			print(request.form)
			to=request.form['address']
			number=int(request.form['amount'])
			public_key=pair[private_key]
			money[private_key]-=number
			for i in range(number):
				pay(public_key,to)
			return "ok"


	@app.route('/guess',methods=['POST'])
	def guess():
		number=request.form['number']
		amount=request.form['amount']
		key=request.cookies.get("key")
		key=b64decode(key)
		database.append((number,key,amount))
		return "ok"

			

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
