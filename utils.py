import os
import requests
from requests import RequestException
import gui


def get_page(url):
	try:
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response.text
		print('链接访问失败，请重试...')
		gui.GUIOperate.write_scrolled_text('链接访问失败，请重试...\n')
		return None
	except RequestException:
		print('链接访问失败，请重试...')
		gui.GUIOperate.write_scrolled_text('链接访问失败，请重试...\n')
		return None


def get_m3u8_content(url, try_count=1):
	if try_count > 3:
		print('Get M3U8 Content Failed ', url)
		insert_text = 'Get M3U8 Content Failed ' + url + '\n'
		gui.GUIOperate.write_scrolled_text(insert_text)
		return None
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
	}
	try:
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response.text
		return get_m3u8_content(url, try_count+1)
	except RequestException:
		return get_m3u8_content(url, try_count+1)


def get_ts(url, try_count=1):
	if try_count > 3:
		print('Get TS Failed ', url)
		insert_text = 'Get TS Failed ' + url + '\n'
		gui.GUIOperate.write_scrolled_text(insert_text)
		return None
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
	}
	try:
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code == 200:
			return response
		return get_ts(url, try_count+1)
	except RequestException:
		return get_ts(url, try_count+1)


def download_ts(m3u8_url, file_line, c_fule_name, download_path, index):
	# 拼出ts片段的URL
	pd_url = m3u8_url.rsplit('/', 1)[0] + '/' + file_line[index + 1]  # rsplit从字符串最后面开始分割
	response = get_ts(pd_url)
	if response:
		if not os.path.exists(download_path):
			os.mkdir(download_path)
		with open(download_path + c_fule_name, 'wb') as f:
			f.write(response.content)
			f.close()
		print('正在下载 ', c_fule_name)
		insert_text = '正在下载 ' + c_fule_name + '\n'
		gui.GUIOperate.write_scrolled_text(insert_text)
