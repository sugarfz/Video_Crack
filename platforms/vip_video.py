from utils import *


def is_valid(url, path):
	if url is '':
		print('请输入视频链接...')
		gui.GUIOperate.write_scrolled_text('请输入视频链接...\n')
		return None
	else:
		url_pattern = re.compile('[a-zA-z]+://[^\s]*', re.S)
		result = re.search(url_pattern, url)
		if result is None:
			print('错误的视频链接，请重新输入...')
			gui.GUIOperate.write_scrolled_text('错误的视频链接，请重新输入...\n')
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


def get_m3u8_url(html):
	pattern = re.compile('<iframe.*?src=.*?url=(.*?)\".*?</iframe>', re.S)
	m3u8_url = re.search(pattern, html)
	if m3u8_url:
		return m3u8_url.group(1)
	else:
		print('未找到视频...')
		gui.GUIOperate.write_scrolled_text('未找到视频...\n')
		return None


def run(url, path, name):
	if is_valid(url, path):  # 判断有效性
		gui.GUIOperate.change_entry_fg('#F5F5F5')
		real_url = 'http://www.wq114.org/tong.php?url=' + url
		html = get_page(real_url)
		if html:
			m3u8_url = get_m3u8_url(html)
			if m3u8_url:
				download_m3u8(m3u8_url, path, name)


if __name__ == '__main__':
	_url = 'http://www.iqiyi.com/v_19rr839kro.html'
	_path = 'E:/PycharmProjects/Video_Crack/video'
	_name = 'movie'
	run(_url, _path, _name)
