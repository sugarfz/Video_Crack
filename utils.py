import os
import re
import shlex
import subprocess
import threading
from tkinter import messagebox
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


# 判断文件是否存在，若文件已存在，是否覆盖
def is_file_exists(path, name, video_count):
	file_path = '{}/{}{}.mp4'.format(path, name, video_count)
	if os.path.exists(file_path):
		title = 'Warning'
		msg = '{}.mp4已存在，是否覆盖？'.format(name)
		ans = messagebox.askokcancel(title, msg)
		if ans is True:
			os.chdir(path)
			del_cmd = 'del /Q {}*.mp4'.format(name)
			os.system(del_cmd)
		else:
			print('下载被中断，请重试...')
			gui.GUIOperate.write_scrolled_text('下载被中断，请重试...\n')
			raise Exception


# 过滤从CMD实时获取的输出
def info_filter(line):
	pat_line = re.compile('.*?(Opening.*?for reading)', re.S)
	pat_show = re.compile('(frame=.*?fps=.*?q=.*?size=.*?time=.*?bitrate=.*?speed=.*?x)', re.S)
	pat_end = re.compile('(video:.*?audio:.*?subtitle:.*?streams:.*?headers:.*?overhead:.*?%)', re.S)
	if re.search(pat_line, line) or re.search(pat_show, line):
		show_lines = re.findall(pat_show, line)
		if show_lines:
			for show_line in show_lines:
				gui.GUIOperate.write_scrolled_text(show_line + '\n')
	if re.search(pat_end, line):
		show_lines = re.findall(pat_end, line)
		if show_lines:
			for show_line in show_lines:
				gui.GUIOperate.write_scrolled_text(show_line + '\n')


sum_time = '00:00:00.00'


# 视频信息显示
def show_video_info(line):
	global sum_time
	pat_video_info = re.compile('Stream #0:[0-1]: Video:.*?,.*?,\s+(\d+x\d+).*?,\s+(\d+.?\d+\s+fps)', re.S)
	pat_sum_time = re.compile('Duration:\s+(.*?),\s+start', re.S)
	pat_already_download = re.compile('L?size=\s*(\d+)kB\s+time=(\d{2}:\d{2}:\d{2}\.\d{2})', re.S)
	pat_download_rate = re.compile('bitrate=\s+(\d+\.?\d*)kbits/s', re.S)
	if re.search(pat_video_info, line):
		dpi = re.search(pat_video_info, line).group(1)
		fps = re.search(pat_video_info, line).group(2)
		gui.GUIOperate.update_video_info(dpi, fps)
	if re.search(pat_sum_time, line):
		sum_time = re.search(pat_sum_time, line).group(1)
		gui.GUIOperate.update_video_sum_time(sum_time)
	if re.search(pat_already_download, line):
		items = re.findall(pat_already_download, line)
		if items:
			for size, now_time in items:
				gui.GUIOperate.update_video_already_download(now_time, float(size))
				gui.GUIOperate.update_progress_bar(sum_time, now_time)
	if re.search(pat_download_rate, line):
		rates = re.findall(pat_download_rate, line)
		if rates:
			for rate in rates:
				gui.GUIOperate.update_video_download_rate(float(rate))


def download_m3u8(m3u8_url, path, name, video_count=''):
	insert_text = '正在下载{}{}...\n'.format(name, video_count)
	print(insert_text)
	gui.GUIOperate.write_scrolled_text(insert_text)
	try:
		if not os.path.exists(path):
			os.makedirs(path)
		is_file_exists(path, name, video_count)
		shell_cmd = 'ffmpeg -i "{}" -c copy "{}/{}{}.mp4"'.format(m3u8_url, path, name, video_count)
		cmd_list = shlex.split(shell_cmd)
		popen = subprocess.Popen(cmd_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		while popen.poll() is None:
			line = popen.stdout.readline().decode('gbk').strip()
			print(line)
			th_video_info = threading.Thread(target=show_video_info, args=(line,))
			th_info_filter = threading.Thread(target=info_filter, args=(line,))
			th_video_info.setDaemon(True)
			th_info_filter.setDaemon(True)
			th_video_info.start()
			th_info_filter.start()
		if popen.returncode != 0:
			print('subprocess failed with code', popen.returncode)
	except KeyboardInterrupt:
		print('下载中止...')
		gui.GUIOperate.write_scrolled_text('下载中止...\n\n')
		messagebox.showerror('提示', '下载中止...')
	else:
		insert_text = '{}{}.mp4下载完成...'.format(name, video_count)
		print(insert_text)
		gui.GUIOperate.write_scrolled_text(insert_text + '\n\n')
		messagebox.showinfo('提示', insert_text)
