from hashlib import sha256
import rsa
import random
import time
from flask import Flask,request
import json
import re
from base64 import b64encode
from base64 import b64decode
import urllib2

def mine(y,hardness):
	while sha256(str(y)).hexdigest()[:hardness]!="0"*hardness:
		y=y+1
	return y

def valid_proof(y,hardness):
	return sha256(str(y)).hexdigest()[:hardness]=="0"*hardness

def hasMoney(chain,node):
	money=0
	data=chain.chain
	for i in data:
		for t in i.transactions:
			if t[0] is node[1]:
				money=money+1
			elif t[1] is node[1]:
				money=money-1
	if money > 0:
		return True
	return False

def shuffle():
	tmp=range(52)
	random.shuffle(tmp)
	l1=tmp[0:13]
	l2=tmp[13:26]
	l3=tmp[26:39]
	l4=tmp[39:52]
	return [l1,l2,l3,l4]



def ask(public_key):
	None
	#send public key	

def get_key(key):
	print('\n\n\n')
	print(key)
	return rsa.PublicKey.load_pkcs1(key) #generate the user's public key to encrypt file

def encrypt(key,stuff):
	return rsa.encrypt(str(stuff),key)	#encrypt the stuff

def decrypt(key,stuff):
	return rsa.decrypt(str(stuff),key)#decrypt the stuff
	
def create_account():
	(public,private)=rsa.newkeys(1024)
	return (public,private)

def sign(private):
	signature = rsa.sign('ok'.encode(),private,'SHA-1')
	return signature

def verify(signature,pub):
	rsa.verify('ok'.encode(),signature,pubkey)
	
def pay(fromUser,toUser):
	data=json.dumps([toUser,fromUser])
	req=urllib2.Request('http://127.0.0.1:5000/transactions',data,{'Content-Type': 'application/json'})
	f=urllib2.urlopen(req)
	f.close()

class Block:
	
	def __init__(self,index,transactions,timestamp,note,previous_hash,proof):
		self.index=index
		self.transactions=transactions
		self.timestamp=timestamp
		self.note=note
		self.previous_hash=previous_hash
		self.proof=proof

	def compute_hash(self):
		block_string=json.dumps(self.__dict__,sort_keys=True)
		return sha256(block_string).hexdigest()

class BlockChain:
	def __init__(self):
		self.hardness=1
		self.chain=[]
		self.unchain=[]
		self.length=0;
		self.firstChain()

	def firstChain(self):
		first_block=Block(0,[],time.time(),dict(),"0",'0')
		first_block.hash=first_block.compute_hash()
		self.chain.append(first_block)

	def last_block(self):
		return self.chain[-1]

	def add2Chain(self,block):
		if not self.last_block().hash is block.previous_hash:
			return False
		if not self.isValid(block):
			return False
		block.hash=block.compute_hash()
		self.chain.append(block)
		self.length=self.length+1
		return True

	def isValid(self,block):
		if valid_proof(block.proof,self.hardness):
			t=block.timestamp
			if abs(t-self.last_block().timestamp)<100:
				self.hardness=self.hardness+1
			elif hardness > 1:
				self.hardness=self.hardness-1
			return True
		return False

	def mine(self):
		result=mine(random.random()*100,self.hardness)
		self.packup(result)

	def packup(self,proof):
		note=dict()
		self.unchain.sort()
		unchain=self.unchain

		i=0;
		tmp=None
		mark=0
		for node in self.unchain:
			if i is 3:
				result=shuffle()
				print(unchain[mark])
				note[unchain[mark][1]]=b64encode(encrypt(get_key(unchain[mark][1]),str(result[0])))
				note[unchain[mark+1][1]]=b64encode(encrypt(get_key(unchain[mark+1][1]),str(result[1])))
				note[unchain[mark+2][1]]=b64encode(encrypt(get_key(unchain[mark+2][1]),str(result[2])))
				note[unchain[mark+3][1]]=b64encode(encrypt(get_key(unchain[mark+3][1]),str(result[3])))
				mark=mark+4
			if node[0] is tmp:
				i=i+1
			else:
				tmp=node[0]
				i=1
		self.unchain=[]
		index=self.last_block().index+1
		previous_hash=self.last_block().hash
		newBlock=Block(index,unchain,time.time(),note,previous_hash,proof)
		self.add2Chain(newBlock)
		for i in self.peers:
			url="http://{}/add_block".format(i)
			requests.post(url,data=json.dumps(block.__dict__,sort_keys=True))

if __name__=='__main__':
	chain=BlockChain()
	chain.peers=set()
	peers=chain.peers
	chain.mine()
	(a,b)=create_account()
	result=a.save_pkcs1()
	tmp=json.dumps([result,result])

