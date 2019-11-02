import pyscreenshot as ImageGrab
import pyperclip
from tqdm import trange
from slugify import slugify
import os
import sys
import pyautogui as pgui
import cv2
import numpy as np
import csv
import json


class AutoPvsys:
	def __init__(self, res_path='res', img_path='img', csv_path='csv'):
		# directory
		self.root = os.path.dirname(os.path.abspath(__file__))
		self.dir_res = os.path.join(self.root, res_path)
		self.dir_img = os.path.join(self.dir_res, img_path)
		self.dir_csv = os.path.join(self.root, csv_path)
		self.dirs = [
			self.dir_res,
			self.dir_img,
			self.dir_csv,
		]
		# files
		self.img_screenshot = os.path.join(self.dir_img, 'screenshot.png')
		self.img_full_graph = os.path.join(self.dir_img, 'full_graph.jpg')
		self.img_temp = os.path.join(self.dir_img, 'temp.jpg')
		self.img_radiation = os.path.join(self.dir_img, 'radiation.jpg')
		self.img_export = os.path.join(self.dir_img, 'export.jpg')
		self.img_copy_value = os.path.join(self.dir_img, 'copy_value.jpg')
		self.img_copy_table = os.path.join(self.dir_img, 'copy_table.jpg')
		self.imgs_screen_1 = {
			'img_full_graph': self.img_full_graph,
			'img_temp': self.img_temp,
			'img_radiation': self.img_radiation,
			'img_copy_table': self.img_copy_table,
		}
		self.imgs_screen_2 = {
			'img_export': self.img_export,
		}
		self.imgs_screen_3 = {
			'img_copy_value': self.img_copy_value
		}
		# variable
		self.slot = 5
		self.img_loc_dict=dict()
		self.img_loc_flag=False
		self.csv_file_name = 'output.csv'
		self.csv_file = os.path.join(self.dir_csv, self.csv_file_name)

		
		

	def folder_check_and_create(self):
		# check resource folders, if not exists, create new one
		for directory in self.dirs:
			if not os.path.exists(directory):
				print('>>created', directory)
				os.makedirs(directory)

	def screenshot(self, save=False):
		print('taking screenshot...', end='')
		im = ImageGrab.grab()
		print('done')
		if not save:
			return im
		# save image file
		im.save(self.img_screenshot)
		return None

	def match_images(self, pattern_set, img_file=None, save_screenshot=False):
		threshold = 0.8
		img_src = None
		# handle screenshot file from external
		if img_file:
			self.img_screenshot = img_file  # load up screenshot from external file
		else:
			img_src = self.screenshot(save=save_screenshot)  # take screen shot

		# load up screenshot
		if img_src:
			img_bgr = np.array(img_src)	 # load direct source from screen
		else:
			img_bgr = cv2.imread(self.img_screenshot)  # load image from saved image
		img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

		for k, img_path in pattern_set.items():
			print('match image...' + k, end=' ')
			template = cv2.imread(img_path, 0)
			w, h = template.shape[::-1]
			res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
			loc = np.where(res >= threshold)
			
			# debug_draw_image_region(img_bgr, loc)
			if loc[0]:
				try:
					pt = list(zip(*loc[::-1]))[0]
					pos = (pt[0], pt[1] + h/2)
					self.img_loc_dict[k] = pos
					print('founded!')
				except:
					print()
					print('!!! Can not locate PVSyst on Desktop !!!')
					sys.exit(0)
			else:
				print('no found')

	# mouse operation
	def mouse_move(self, xy, duration=0.25):
		x = xy[0]
		y = xy[1]
		pgui.moveTo(x, y, duration=duration)

	def mouse_click(self, xy, duration=0.25):
		x = xy[0]
		y = xy[1]
		pgui.click(x, y, duration=duration)
		# pgui.PAUSE = 0.5

	#  keybaord operation
	def keyboard_enter(self):
		pgui.press('enter')

	def keybaord_close_window(self):
		pgui.hotkey('altleft', 'f4')

	def keyboard_typewrite(self, value):
		pgui.typewrite(value)
		pgui.press('enter')

	def keyboard_clear_value(self):
		pgui.press('enter')
		pgui.press('delete')

	def keyboard_tab(self):
		pgui.press('tab')

	def update_image_button_location(self):
		if self.img_loc_flag:
			print('all image already up to date')
			return

		self.match_images(self.imgs_screen_1)
		# update 2nd screen
		full_graph_pos = self.img_loc_dict.get('img_full_graph')
		if full_graph_pos:
			self.mouse_click(full_graph_pos)
			self.match_images(self.imgs_screen_2)
			# update 3rd screen
			export_pos = self.img_loc_dict.get('img_export')
			if export_pos:
				self.mouse_click(export_pos)
				self.match_images(self.imgs_screen_3)
				# exit current windows
				self.keybaord_close_window()
				self.img_loc_flag = True
				print('all image locations updated')

	# operations
	def update_temp(self, value):
		value = str(value)
		pos = self.img_loc_dict.get('img_temp')
		if pos:
			self.mouse_click(pos)
			self.keyboard_clear_value()
			self.keyboard_typewrite(value)

	def update_irradiation(self, values, place_holder=5):
		slots = ['0']*place_holder
		for i, value in enumerate(values):
			slots[i] = str(value)
		pos = self.img_loc_dict.get('img_radiation')
		if pos:
			self.mouse_click(pos)
			for value in slots:
				self.keyboard_clear_value()
				self.keyboard_typewrite(value)
				self.keyboard_tab()

	def update_pan_file_name(self):
		pos = self.img_loc_dict.get('img_copy_table')
		if pos:
			self.mouse_click(pos)
			self.keyboard_enter()
			txt = pyperclip.paste()
			txt = txt.split('.PAN')[0]
			file_name = slugify(txt) + '.csv'
			self.csv_file_name = file_name
			self.csv_file = os.path.join(self.dir_csv, self.csv_file_name)

	def get_export_data(self):
		if self.img_loc_flag:
			self.mouse_click(self.img_loc_dict.get('img_full_graph'))
			self.mouse_click(self.img_loc_dict.get('img_export'))
			self.mouse_click(self.img_loc_dict.get('img_copy_value'))
			self.keyboard_enter()
			self.keybaord_close_window()
			return pyperclip.paste()

	def parse_data(self, raw_data, temp_data, irra_data):
		if not raw_data:
			return None
		data_arr = raw_data.split('Curve no')
		data_points = []
		results = []
		for data in data_arr:
			data = data.strip()
			if data:
				points = data.split(';')
				point = points[-3].strip()
				data_points.append(point)

		for i in range(len(irra_data)):
			result = {
				'tmp': temp_data,
				'irr': irra_data[i],
				'val': data_points[i]
			}
			results.append(result)
		return results

	def save_data(self, data):
		if not data:
			return
		if not os.path.exists(self.csv_file):
			fileEmpty = True
		else:
			fileEmpty = os.stat(self.csv_file).st_size == 0
		fields = list(data[0].keys())
		with open(self.csv_file, 'a') as f:
			writer = csv.DictWriter(f, lineterminator='\n', fieldnames=fields)
			if fileEmpty:
				writer.writeheader()
			for d in data:
				writer.writerow(d)

	def read_txt_to_json(self, file_name='config.txt'):
		txt_file = os.path.join(self.root, file_name)
		with open(txt_file) as f:
			data = json.loads(f.read())
			return data


if __name__ == '__main__':
	
	# init
	irra_arr = []
	count = 0

	agent = AutoPvsys()
	agent.folder_check_and_create()
	agent.update_image_button_location()
	agent.update_pan_file_name()
	param = agent.read_txt_to_json() # read from config.txt

	min_temp = int(param.get('min_temp'))
	max_temp = int(param.get('max_temp'))
	temp_step = int(param.get('temp_step'))
	min_irra = int(param.get('min_irra'))
	max_irra = int(param.get('max_irra'))
	irra_step = int(param.get('irra_step'))


	for temp in trange(min_temp, max_temp+temp_step, temp_step, leave=True, desc='temp'):
		for irra in trange(min_irra, max_irra+irra_step, irra_step, leave=True, desc='irra'):
			count += 1
			irra_arr.append(irra)
			if (count == agent.slot) or (irra >= max_irra) or (temp >= max_temp and irra >= max_irra):
				agent.update_temp(temp)
				agent.update_irradiation(irra_arr)
				raw_data = agent.get_export_data()
				parsed_data = agent.parse_data(raw_data, temp, irra_arr)
				agent.save_data(parsed_data)
				count = 0
				irra_arr = []


