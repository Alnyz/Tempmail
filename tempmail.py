# -*- coding: utf-8 -*-
import hashlib
import requests
import time
import cfscrape
from datetime import datetime
from json import dumps
from urllib.request import unquote
from random import choice

class TempsMail(object):	
	def __init__(self):
		self._session = requests.Session()
		self.API_HOST = "https://api2.temp-mail.org"
		self.BASE_URI = "https://temp-mail.org/"
		self.list_headers = [
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
			"Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
			"Googlebot/2.1 (+http://www.google.com/bot.html)"
		]
		self._headers = {"User-Agent":choice(self.list_headers)}
		self._session.headers.update(self._headers)
		self._wraper = cfscrape.create_scraper(sess=self._session, delay=5)
		
	def email_to_md5(self, email: str):
		return hashlib.md5("{email}". \
							format(email=email).encode('utf-8')).hexdigest()
							
	def get_email(self):
		req = self._wraper.get(url=self.BASE_URI)
		if req.ok:
			cok = req.cookies.get_dict()
			mail = unquote(cok.get("mail", None))
			return mail
			
	def waiting_message(self, mail):
		md5 = self.email_to_md5(mail)
		req = requests.get(self.API_HOST+"/request/mail/id/"+md5+'/format/json',
									headers=self._headers)
		data = req.json()
		datas = {}
		text = ""
		if "error" in data:
			return data
		for i in data:
			from_ = i["mail_from"].strip()
			date = datetime.ctime(datetime.fromtimestamp(i["mail_timestamp"]))
			subject = i["mail_subject"]
			msg = i["mail_text"]
			text += "Incoming email: \
				\nFrom: {from_} \
				\nDate: {date} \
				\nSubject: {subject} \
				\nMessage: {msg}".format(from_=from_, date=date, subject=subject, msg=msg)
		return text

if __name__ == "__main__":		
	t = TempsMail()
	mail = t.get_email()
	print("There is your mail:", end="\n")
	print("="*(len(mail) + 1))
	print(mail)
	print("="*(len(mail) + 1))
	while 1:
		data = t.waiting_message(mail)
		if "error" in data:
			time.sleep(2)
			continue
		else:
			print(data)
			
