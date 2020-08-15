import tkinter as tk
import mosaic

class Application(tk.Frame):
	"""A simple GUI for mosaic.py"""
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()


	def create_widgets(self):
		self.source_dir_label = tk.Label(self, text='Source directory')
		self.source_dir_label.grid(row=0, column=0)
		self.source_dir = tk.Entry(self)
		# self.source_dir.insert(0, 'Type here')
		self.source_dir.grid(row=0, column=1)

		self.source_img_label = tk.Label(self, text='Source image')
		self.source_img_label.grid(row=1, column=0)
		self.source_img = tk.Entry(self)
		self.source_img.grid(row=1, column=1)

		self.number_label = tk.Label(self, text='Images per row')
		self.number_label.grid(row=2, column=0)
		self.number = tk.Entry(self)
		self.number.grid(row=2, column=1)

		self.width_label = tk.Label(self, text='Width of images')
		self.width_label.grid(row=3, column=0)
		self.width = tk.Entry(self)
		self.width.grid(row=3, column=1)

		self.make = tk.Button(self)
		self.make['text'] = 'Make Mosaic!'
		self.make['command'] = self.make_mosaic
		self.make.grid(row=4, column=0, columnspan=2)

		self.quit = tk.Button(self, text='QUIT', fg='red', command=self.master.destroy)
		self.quit.grid(row=5, column=0, columnspan=2)


	def make_mosaic(self):
		mosaic.mosaic(self.source_dir.get(), self.source_img.get(), '', int(self.number.get()), int(self.width.get()))


if __name__ == '__main__':
	root = tk.Tk()
	app = Application(master=root)
	app.mainloop()
