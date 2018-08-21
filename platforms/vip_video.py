import json
import re
from urllib.parse import unquote
from utils import *


def get_m3u8_url(html):
	pattern = re.compile('<iframe.*?src=.*?url=(.*?)\".*?</iframe>', re.S)
	m3u8_url = re.search(pattern, html)
	if m3u8_url:
		return m3u8_url.group(1)
	return None


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
	html = get_page(real_url)
	if html:
		m3u8_url = get_m3u8_url(html)
		if m3u8_url:
			download_m3u8(m3u8_url, path)
	

if __name__ == '__main__':
	_url = 'http://www.iqiyi.com/v_19rr839kro.html'
	_path = 'E:/PycharmProjects/Video_Crack/video'
	run(_url, _path)
