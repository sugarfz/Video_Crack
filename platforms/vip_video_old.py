import json
import re
from urllib.parse import unquote
from utils import *
from pyquery import PyQuery as pq


def parse_src_page(html):
	doc = pq(html)
	return doc('iframe').attr('src')


def parse_cont_page(html):
	pattern = re.compile('<script.*?vipjiexi.*?url.*?\'(.*?)\'.*?</script>', re.S)
	con_url = re.search(pattern, html)
	if con_url:
		return con_url.group(1)
	return None


def get_m3u8_url(url, try_count=1):
	if try_count > 3:
		return None
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
	}
	data = {
		'url': url,
		'up': '0'
	}
	url = 'http://www.wq114.org/x2/api.php'
	try:
		response = requests.post(url, headers=headers, data=data, timeout=30)
		if response.status_code == 200:
			data = json.loads(response.text)  # 转化为字典
			if data and 'url' in data.keys():
				return unquote(data.get('url'))
			return None
		return get_m3u8_url(url, try_count + 1)
	except RequestException:
		return get_m3u8_url(url, try_count + 1)


def download_m3u8(m3u8_url, path):
	print('准备下载...')
	download_path = path + '/'
	try:
		all_content = get_m3u8_content(m3u8_url)
		file_line = all_content.split('\n')  # 读取文件里的每一行
		# 通过判断文件头来确定是否是M3U8文件
		if file_line[0] != '#EXTM3U':
			raise BaseException('非M3U8链接')
		else:
			unknow = True  # 用来判断是否找到了下载的地址
			threads = []  # 定义线程池
			for index, line in enumerate(file_line):
				if 'EXTINF' in line:
					unknow = False
					c_fule_name = str(file_line[index + 1])
					download_ts(m3u8_url, file_line, c_fule_name, download_path, index,)
			if unknow:
				raise BaseException('未找到对应的下载链接')
			else:
				print('下载完成，正在合并视频流...')
				# gui.GUIOperate.write_scrolled_text('下载完成，正在合并视频流...\n')
				merge_file(download_path)
	except Exception:
		return None


def merge_file(download_path):
	os.chdir(download_path)  # 修改当前工作目录
	video_name = 'out.mp4'
	merge_cmd = 'copy /b *.ts ' + video_name
	del_cmd = 'del /Q *.ts'
	os.system(merge_cmd)
	os.system(del_cmd)
	print('合并完成，请欣赏 ', video_name)
	insert_text = '合并完成，请欣赏 ' + video_name + '\n\n'
	# gui.GUIOperate.write_scrolled_text(insert_text)


def run(url, path):
	real_url = 'http://www.wq114.org/tong.php?url=' + url
	src_html = get_page(real_url)
	if src_html:
		src_url = parse_src_page(src_html)
		if src_url:
			src_url = 'http://www.wq114.org/' + src_url
			cont_html = get_page(src_url)
			if cont_html:
				cont_url = parse_cont_page(cont_html)
				if cont_url:
					m3u8_url = get_m3u8_url(cont_url)
					if m3u8_url:
						download_m3u8(m3u8_url, path)
					

if __name__ == '__main__':
	_url = 'http://www.iqiyi.com/v_19rr839kro.html'
	_path = 'E:/PycharmProjects/Video_Crack/video'
	run(_url, _path)
