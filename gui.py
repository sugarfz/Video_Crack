import os
import signal
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from tkinter.filedialog import askdirectory
import base64
from pictures.cat_logo import img as logo
from platforms import *


class GUIOperate(object):
	# 运行GUI
	@staticmethod
	def gui_loop():
		try:
			top.mainloop()
		except KeyboardInterrupt:
			print('下载中止...')
			GUIOperate.write_scrolled_text('下载中止...\n')
			GUIOperate.gui_loop()
	
	# 写入滚动文本框
	@staticmethod
	def write_scrolled_text(text):
		scrolled_text.insert(INSERT, text)
		scrolled_text.see(END)
	
	# 改变输入框文本颜色
	@staticmethod
	def change_entry_fg(colour):
		entry_url['fg'] = colour
		entry_name['fg'] = colour

	# 更新视频信息
	@staticmethod
	def update_video_info(dpi, fps):
		var_video_info.set('[视频信息:  {}, {}]'.format(dpi, fps))
	
	# 更新视频总时长
	@staticmethod
	def update_video_sum_time(time):
		var_video_total_time.set('[总时长:  {}]'.format(time))
	
	# 更新已下载视频时长和大小
	@staticmethod
	def update_video_already_download(time, size):
		var_video_already_download.set('[已下载:  %s, %.2f MB]' % (time, size/1024))
	
	# 更新下载速率
	@staticmethod
	def update_video_download_rate(bit_rate):
		byte_rate_KB = bit_rate/8
		byte_rate_MB = byte_rate_KB/1024
		if byte_rate_MB > 1:
			var_video_download_rate.set('[%.2f  MB/s]' % byte_rate_MB)
		else:
			var_video_download_rate.set('[%.2f  KB/s]' % byte_rate_KB)
	
	# 更新进度条
	@staticmethod
	def update_progress_bar(sum_time, now_time):
		sum_length = 90
		sum_items = sum_time.split(':')
		now_items = now_time.split(':')
		sum_times = float(sum_items[0])*60*60 + float(sum_items[1])*60 + float(sum_items[2])
		now_times = float(now_items[0])*60*60 + float(now_items[1])*60 + float(now_items[2])
		green_length = int(sum_length*now_times/sum_times)
		percent = 100*now_times/sum_times
		if abs(percent - 100) < 0.5:
			percent = 100
			green_length = sum_length
		label_progress_bar_fg.config(bg='#06B025', width=green_length)
		var_progress_bar_percent.set('%.2f  %%' % percent)


def download():
	url = entry_url.get()
	path = entry_path.get()
	name = entry_name.get()
	scrolled_text.delete('1.0', END)
	if name == file_name:
		name = 'video'  # 默认文件名
	video_platform = var_option_menu.get()
	if video_platform == options[0]:
		th = threading.Thread(target=zhihu_video.run, args=(url, path, name))
	else:
		th = threading.Thread(target=vip_video.run, args=(url, path, name))
	th.setDaemon(True)
	th.start()


def stop():
	os.kill(0, signal.CTRL_C_EVENT)


def select_path():
	_path = askdirectory()
	var_path_text.set(_path)


# 顶层窗口
top = Tk()  # 创建顶层窗口
top.title('视频下载器 - 1.0    by:  sugarfz')
top.geometry('800x500+290+100')  # 初始化窗口大小
top.resizable(False, False)  # 窗口长宽不可变
top.config(bg='#535353')

# 插入背景图片(Label)
tmp = open('logo.gif', 'wb+')  # 临时文件用来保存gif文件
tmp.write(base64.b64decode(logo))
tmp.close()
image = Image.open('logo.gif')
bg_img = ImageTk.PhotoImage(image)
label_img = Label(top, image=bg_img, bg='#535353', cursor='spider')

# 视频链接(Label+Entry)
label_url = Label(top, text='视频链接', fg='#F5F5F5', bg='#535353', cursor='cross')
var_url_text = StringVar()
entry_url = Entry(top, relief=SUNKEN, fg='gray', bg='#3A3A3A', bd=2, width=60, textvariable=var_url_text, insertbackground='#F5F5F5', insertborderwidth=1)

# 下载路径(Label+Entry+Button)
label_path = Label(top, text='下载路径', fg='#F5F5F5', bg='#535353', cursor='cross')
var_path_text = StringVar()
entry_path = Entry(top, relief=SUNKEN, fg='#F5F5F5', bg='#3A3A3A', bd=2, width=51, textvariable=var_path_text, insertbackground='#F5F5F5', insertborderwidth=1)
button_choice = Button(top, relief=RAISED, text='打开', fg='#F5F5F5', bg='#7A7A7A', bd=1, width=5, height=1, command=select_path, activebackground='#F5F5F5', activeforeground='#535353')

# 视频平台选择(Label+OptionMenu)
label_option = Label(top, text='视频平台', fg='#F5F5F5', bg='#535353', cursor='cross')
options = ['1.知乎', '2.爱奇艺']
var_option_menu = StringVar()
var_option_menu.set(options[0])
option_menu = OptionMenu(top, var_option_menu, *options)
option_menu.config(bd=0, fg='#3A3A3A', bg='#F5F5F5', relief=GROOVE)
option_menu['menu'].config(fg='#3A3A3A', bg='#F5F5F5', activebackground='#7A7A7A', activeforeground='#F5F5F5')

# 视频名称(Label+Entry)
label_name = Label(top, text='输入文件名', fg='#F5F5F5', bg='#535353', cursor='cross')
var_name_text = StringVar()
entry_name = Entry(top, relief=SUNKEN, fg='gray', bg='#3A3A3A', bd=2, width=21, textvariable=var_name_text, insertbackground='#F5F5F5', insertborderwidth=1)

# 下载/停止/退出按钮
button_start = Button(top, text='下载', fg='#F5F5F5', bg='#7A7A7A', command=download, height=1, width=15, relief=GROOVE, bd=2, activebackground='#F5F5F5', activeforeground='#535353')
button_stop = Button(top, text='停止', fg='#F5F5F5', bg='#7A7A7A', command=stop, height=1, width=15, relief=GROOVE, bd=2, activebackground='#F5F5F5', activeforeground='#535353')
button_quit = Button(top, text='退出', fg='#F5F5F5', bg='#7A7A7A', command=top.quit, height=1, width=15, relief=GROOVE, bd=2, activebackground='#F5F5F5', activeforeground='#535353')

# 视频信息(Label)
label_video_title = Label(top, text='信息显示:', fg='#F5F5F5', bg='#535353')
var_video_info = StringVar()
label_video_info = Label(top, textvariable=var_video_info, fg='#F5F5F5', bg='#535353')
var_video_total_time = StringVar()
label_video_total_time = Label(top, textvariable=var_video_total_time, fg='#F5F5F5', bg='#535353')
var_video_already_download = StringVar()
label_video_already_download = Label(top, textvariable=var_video_already_download, fg='#F5F5F5', bg='#535353')
var_video_download_rate = StringVar()
label_video_download_rate = Label(top, textvariable=var_video_download_rate, fg='#F5F5F5', bg='#535353')

# 可滚动的多行文本区域
scrolled_text = ScrolledText(top, relief=GROOVE, bd=2, height=18, width=110, xscrollcommand=True, font=('', 9), fg='#F5F5F5', bg='#3A3A3A', cursor='heart', insertbackground='#F5F5F5', insertborderwidth=1)

# 进度条
label_progress_bar_bg = Label(top, height=1)
label_progress_bar_fg = Label(top, height=1)
var_progress_bar_percent = StringVar()
label_progress_bar_percent = Label(top, textvariable=var_progress_bar_percent, fg='#F5F5F5', bg='#535353')

# ********************place布局********************
# 背景图片
label_img.place(relx=0.5, rely=0.08, anchor=CENTER)
# 视频链接
label_url.place(relx=0.1, rely=0.17, anchor=CENTER)
entry_url.place(relx=0.42, rely=0.17, anchor=CENTER)
# 下载路径
label_path.place(relx=0.1, rely=0.26, anchor=CENTER)
entry_path.place(relx=0.38, rely=0.26, anchor=CENTER)
button_choice.place(relx=0.655, rely=0.26, anchor=CENTER)
# 视频平台选择
label_option.place(relx=0.1, rely=0.36, anchor=CENTER)
option_menu.place(relx=0.2, rely=0.36, anchor=CENTER)
# 视频名称
label_name.place(relx=0.36, rely=0.36, anchor=CENTER)
entry_name.place(relx=0.51, rely=0.36, anchor=CENTER)
# 下载/停止/退出按钮
button_start.place(relx=0.82, rely=0.17, anchor=CENTER)
button_stop.place(relx=0.82, rely=0.26, anchor=CENTER)
button_quit.place(relx=0.82, rely=0.36, anchor=CENTER)
# 视频信息
label_video_title.place(relx=0.102, rely=0.45, anchor=CENTER)
label_video_info.place(relx=0.262, rely=0.45, anchor=CENTER)
label_video_total_time.place(relx=0.472, rely=0.45, anchor=CENTER)
label_video_already_download.place(relx=0.687, rely=0.45, anchor=CENTER)
label_video_download_rate.place(relx=0.867, rely=0.45, anchor=CENTER)
# 可滚动的多行文本区域
scrolled_text.place(relx=0.497, rely=0.7, anchor=CENTER)
# 进度条
label_progress_bar_bg.place(relx=0.07, rely=0.95, anchor=W)
label_progress_bar_fg.place(relx=0.07, rely=0.95, anchor=W)
label_progress_bar_percent.place(relx=0.897, rely=0.95, anchor=CENTER)

# 输入框默认内容
var_url_text.set(r'请输入文章或视频链接...')

save_path = '/'.join(os.getcwd().split('\\')) + '/video'
if not os.path.exists(save_path):
	os.makedirs(save_path)
var_path_text.set(save_path)

file_name = '默认文件名：video'
var_name_text.set(file_name)

var_video_info.set('[视频信息:  dpi, fps]')
var_video_total_time.set('[总时长:  00:00:00.00]')
var_video_already_download.set('[已下载:  00:00:00.00, 0.00 MB]')
var_video_download_rate.set('[0.00  KB/s]')

scrolled_text.insert(INSERT, '等待下载任务...\n')
scrolled_text.see(END)

label_progress_bar_bg.config(bg='#E6E6E6', width=90)
label_progress_bar_fg.config(bg='#E6E6E6', width=0)
var_progress_bar_percent.set('00.00  %')
