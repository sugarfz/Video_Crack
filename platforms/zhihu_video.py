import json
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
	except RequestException:
		return None


def run(url, path, name):
	video_count = 0
	options = ['高清HD', '标清SD', '普清LD']
	video_dpi_str = options[0][-2:].lower()  # 默认下载高清
	if is_valid(url, path):  # 判断有效性
		# 改变输入框文本颜色
		gui.GUIOperate.change_entry_fg('#F5F5F5')
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
							download_m3u8(m3u8_url, path, name, str(video_count))


if __name__ == '__main__':
	_url = 'https://www.zhihu.com/question/279405182/answer/410204397'
	_path = 'E:/PycharmProjects/Video_Crack/video'
	_name = 'video'
	run(_url, _path, _name)
