#coding:utf-8

import sys
import urllib.request
import urllib.parse
import json
import datetime
import time
import base64

# nasne2syoboi.py
# usage:python nasne2syoboi.py nasneurl userid password
# nasneの予約リストをしょぼいカレンダーに同期します

def translateARIB(str):
	#ARIB外字変換
	aribtbl={
		int('0xE0F8',16): u'[HD]',
		int('0xE0F9',16): u'[SD]',
		int('0xE0FA',16): u'[P]',
		int('0xE0FB',16): u'[W]',
		int('0xE0FC',16): u'[MV]',
		int('0xE0FD',16): u'[手]',
		int('0xE0FE',16): u'[字]',
		int('0xE0FF',16): u'[双]',
		int('0xE180',16): u'[デ]',
		int('0xE181',16): u'[Ｓ]',
		int('0xE182',16): u'[二]',
		int('0xE183',16): u'[多]',
		int('0xE184',16): u'[解]',
		int('0xE185',16): u'[SS]',
		int('0xE186',16): u'[B]',
		int('0xE187',16): u'[N]',
		int('0xE18A',16): u'[天]',
		int('0xE18B',16): u'[交]',
		int('0xE18C',16): u'[映]',
		int('0xE18D',16): u'[無]',
		int('0xE18E',16): u'[料]',
		int('0xE190',16): u'[前]',
		int('0xE191',16): u'[後]',
		int('0xE192',16): u'[再]',
		int('0xE193',16): u'[新]',
		int('0xE194',16): u'[初]',
		int('0xE195',16): u'[終]',
		int('0xE196',16): u'[生]',
		int('0xE197',16): u'[販]',
		int('0xE198',16): u'[声]',
		int('0xE199',16): u'[吹]',
		int('0xE19A',16): u'[PV]',
		int('0xE19B',16): u'[秘]',
		int('0xE19C',16): u'[他]',
	}
	return str.translate(aribtbl)

def changeChNameForSyoboi(name):
	if name=='ＢＳ１１イレブン':
		return 'ＢＳ１１デジタル'
	if name=='ディーライフ':
		return 'Ｄｌｉｆｅ'
	return name

def testShowItem(item):
	for i in range(len(item)):
		for key in item[i]:
			value=item[i][key]
			if key=='title':
				value=translateARIB(value)
			print('%s:%s' % (key,value))

if __name__ == '__main__':
	# Get from Nasne
	address_nasne=sys.argv[1]
	userid=sys.argv[2]
	password=sys.argv[3]
	print('%s,%s,%s' % (address_nasne,userid,password))
	url_nasne='http://'+address_nasne+':64220/schedule/reservedListGet?'
	params_nasne={
				'searchCriteria' : 0,
				'filter' : 0,
				'startingIndex' : 0,
				'requestedCount' : 0,
				'sortCriteria' : 1,
				'withDescriptionLong' : 0,
				'withUserData' : 0
			}
	response_nasne=urllib.request.urlopen(url_nasne + urllib.parse.urlencode(params_nasne))
	json_str_nasne=response_nasne.read()
	data_nasne=json.loads(json_str_nasne)
	item_nasne=data_nasne['item']
	# testShowItem(item)
	devicename='nasne'
	schdatastr=''
	subtitle='subtitle'
	offset='0'
	xid='0'
	for i in range(len(item_nasne)):
		title=translateARIB(item_nasne[i]['title'])
		startTime=datetime.datetime.strptime(item_nasne[i]['startDateTime'],'%Y-%m-%dT%H:%M:%S+09:00')
		endTime=startTime+datetime.timedelta(seconds=int(item_nasne[i]['duration']))
		channelName=changeChNameForSyoboi(item_nasne[i]['channelName'])
		schdata=[]
		schdata.append(str(int(time.mktime(startTime.timetuple()))))
		schdata.append(str(int(time.mktime(endTime.timetuple()))))
		schdata.append(devicename)
		schdata.append(title)
		schdata.append(channelName)
		schdata.append(subtitle)
		schdata.append(offset)
		schdata.append(xid)
		schdatastr+='	'.join(schdata)
		schdatastr+='\n'
	#print(schdatastr)
	# Post to Syoboi
	url_syoboi='http://cal.syoboi.jp/sch_upload'
	headers={}
	headers["authorization"]="Basic " + base64.b64encode((userid + ":" + password).encode('utf-8')).decode('utf-8')
	params_syoboi={
		'data' : schdatastr,
		'slot' : 0,
		'devcolors' : "nasne=#0000ff",
		'epgurl' : '',
	}
	postdata=urllib.parse.urlencode(params_syoboi).encode("utf-8")
	request=urllib.request.Request(url=url_syoboi, headers=headers, data=postdata)
	response=urllib.request.urlopen(request)
	# print(response.read())
