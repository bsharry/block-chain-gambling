from helper import *
from flask import Flask,request
import json
from flask import *

money=dict()

pair=dict()

database=list()

useless=[]

listofcard=dict()

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
		global database
		print("database is ")
		print(database)
		for i in database:
			print(i)
			m=i[1]
			if awesome(i[0],result):
				money[m]+=int(i[2])
			else:
				money[m]-=int(i[2])
		database=[]
		for i in useless:
			if hasattr(chain.chain[-1].note,i[0]):
				pkey=i[i]
				key=get_pkey(i[1])
				result=decrypt(key,chain.chain[-1].note[i[0]])
				listofcard[pkey]=result
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
		money[public_key.save_pkcs1()]=1000
		tmp['public_key']=b64encode(public_key.save_pkcs1())
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
				print(chain.chain[-1].note)
				print(pair)
				pub=pair[private_key]
				print(private_key)
				#print(hasattr(chain.chain[-1].note,pub.decode()))
				print(chain.chain[-1].note.has_key(pub))
				if chain.chain[-1].note.has_key(pub):
					aaa=chain.chain[-1].note
					aaa=aaa[pub]
					aaa=decrypt(get_pkey(private_key),b64decode(aaa))
					print(aaa)
					resp=make_response(render_template("main.html",balance=str(money[pub]),cards=str(aaa)))
					#resp.set_cookie("key",b64encode(private_key))
					return resp
				return render_template("main.html",balance=str(money[pub]))
			return "please log in"
		else:
			private_key=b64decode(request.form['passwd'])
			print(money)
			pub=pair[private_key]
			balance=money[pub]
			print(balance)
			if hasattr(listofcard,private_key):
				print(listofcard[private_key])
				resp=make_response(render_template("main.html",balance=str(money[pub]),cards=str(listofcard[private_key])))
				resp.set_cookie("key",b64encode(private_key))
				return resp
			resp=make_response(render_template("main.html",balance=str(money[pub]),cards="NO CARD SHUFFLED"))
			resp.set_cookie("key",b64encode(private_key))
			return resp

	@app.route('/want',methods=['GET'])
	def pay_you():
		if request.cookies.get("key"):
			private_key=b64decode(request.cookies.get("key"))
			public_key=pair[private_key]
			money[public_key]+=100
			return 'ok'
		return 'failed'

	@app.route('/logout',methods=['GET'])
	def logout():
		response=make_response('logout successfully')
		response.delete_cookie('key')
		return response

	@app.route('/pay',methods=['POST'])
	def pay_tmp():
		if request.cookies.get("key"):
			private_key=b64decode(request.cookies.get("key"))
			print(request.form)
			to=b64decode(request.form['address'])
			number=int(request.form['amount'])
			public_key=pair[private_key]
			money[public_key]-=number
			money[to]+=number
			for i in range(number):
				pay(public_key,to)
			return "ok"


	@app.route('/guess',methods=['POST'])
	def guess():
		number=request.form['number']
		amount=request.form['amount']
		key=request.cookies.get("key")
		key=b64decode(key)
		key=pair[key]
		global database
		database.append((number,key,amount))
		return "ok"

	@app.route("/shuffle",methods=['POST','GET'])
	def nnn():
		if request.method=='POST':
			key=request.cookies.get("key")
			key=b64decode(key)
			pub=pair[key]
			pay(pub,"shuffle")
			useless.append((pub,key))
			return 'ok'

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
