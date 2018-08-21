import re
import json
import threading
from utils import *


def is_valid(url, path):
	if url is '':
		print('请输入文章链接...')
		gui.GUIOperate.write_scrolled_text('请输入文章链接...\n')
		return None
	else:
		url_pattern = re.compile('^(https://www.zhihu.com/question/\d{8,9}/answer/\d{9})$', re.S)
		result = re.search(url_pattern, url)
		if result is None:
			print('错误的文章链接，请重新输入...')
			gui.GUIOperate.write_scrolled_text('错误的文章链接，请重新输入...\n')
			return None
		else:
			if path is '':
				print('请输入视频保存路径...')
				gui.GUIOperate.write_scrolled_text('请输入视频保存路径...\n')
				return None
			else:
				path_pattern = re.compile('(^[a-zA-Z]:/[0-9a-zA-Z_]+(/[0-9a-zA-Z_]+)*$)|(^[a-zA-Z]:/[0-9a-zA-Z_]*$)', re.S)
				result = re.search(path_pattern, path)
				if result is None:
					print('错误的文件路径，请重新输入...')
					gui.GUIOperate.write_scrolled_text('错误的文件路径，请重新输入...\n')
					return None
				else:
					return True


def parse_page(html):
	videos = re.findall(r'z-ico-video"></span>(.*?)</span>', html)
	if videos:
		insert_text = '共找到' + str(len(videos)) + '个视频\n'
		print(insert_text)
		gui.GUIOperate.write_scrolled_text(insert_text)
		for video in videos:
			yield video
	else:
		print('未找到视频')
		gui.GUIOperate.write_scrolled_text('未找到视频\n')


def get_real_url(url, try_count=1):
	if try_count > 3:
		return None
	try:
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		response = requests.get(url, headers=headers, timeout=30)
		if response.status_code >= 400:
			return get_real_url(url, try_count+1)
		return response.url
	except RequestException:
			return get_real_url(url, try_count+1)


def get_m3u8_url(url, video_dpi):
	try:
		path_pattern = re.compile('(\d+)', re.S).search(url).group(1)
		get_play_url = 'https://lens.zhihu.com/api/videos/' + path_pattern
		headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
		}
		content = requests.get(get_play_url, headers=headers).text
		data = json.loads(content)  # 将json格式的字符串转化为字典
		if data and 'playlist' in data.keys():
			m3u8_url = data.get('playlist').get(video_dpi).get('play_url')
			return m3u8_url
	except Exception:
		return None


def download_m3u8(m3u8_url, video_url, video_count, path, video_dpi_str):
	print('准备下载 ', video_url)
	insert_text = '准备下载 ' + video_url + '\n'
	gui.GUIOperate.write_scrolled_text(insert_text)
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
					c_fule_name = str(file_line[index + 1]).split('?', 1)[0]
					source_path = c_fule_name.split('-', 1)[0]  # 区分不同源的视频流
					th = threading.Thread(target=download_ts, args=(m3u8_url, file_line, c_fule_name, download_path, index,))
					threads.append(th)
			if unknow:
				raise BaseException('未找到对应的下载链接')
			else:
				for t in threads:  # 启动线程
					t.start()
				for t in threads:  # 等待子线程结束
					t.join()
				print('下载完成，正在合并视频流...')
				gui.GUIOperate.write_scrolled_text('下载完成，正在合并视频流...\n')
				merge_file(download_path, source_path, video_count, video_dpi_str)
	except Exception:
		return None


def merge_file(download_path, source_path, video_count, video_dpi_str):
	os.chdir(download_path)  # 修改当前工作目录
	video_name = 'video' + str(video_count) + '_' + video_dpi_str + '_' + source_path + '.mp4'
	merge_cmd = 'copy /b ' + source_path + '*.ts ' + video_name
	del_cmd = 'del /Q ' + source_path + '*.ts'
	os.system(merge_cmd)
	os.system(del_cmd)
	print('合并完成，请欣赏 ', video_name)
	insert_text = '合并完成，请欣赏 ' + video_name + '\n\n'
	gui.GUIOperate.write_scrolled_text(insert_text)


def run(url, path, video_dpi):
	video_count = 0
	video_dpi_str = video_dpi[-2:].lower()
	if is_valid(url, path):  # 判断有效性
		# 改变输入框文本颜色
		gui.GUIOperate.change_entry_fg('black')
		html = get_page(url)
		if html:
			video_urls = parse_page(html)
			for video_url in video_urls:
				if video_url:
					real_url = get_real_url(video_url)
					if real_url:
						m3u8_url = get_m3u8_url(real_url, video_dpi_str)
						if m3u8_url:
							video_count += 1
							download_m3u8(m3u8_url, video_url, video_count, path, video_dpi_str)


if __name__ == '__main__':
	_url = 'https://www.zhihu.com/question/279405182/answer/410204397'
	_path = 'E:/PycharmProjects/Video_Crack/video'
	_video_dpi = '标清SD'
	run(_url, _path, _video_dpi)
