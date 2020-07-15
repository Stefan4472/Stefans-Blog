import tkinter as tk
from PIL import Image, ImageTk

MAX_SCREEN_WIDTH: int = 1000
MAX_SCREEN_HEIGHT: int = 600

# REQD_FEATURED_SIZE = (1500, 810)
# REQD_WIDE_BANNER_SIZE = (1900, 300)
# REQD_BANNER_NARROW_SIZE = 

# root = Tk()


# root.mainloop()

# # ... overwrite json file?

class ImageCropper(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        # self.pack()
        # self.createWidgets()
        # ... user chooses file from directory
        img_path: str = 'cpp_game_screenshot_2.jpg'

        raw_image = Image.open(img_path)
        if raw_image.width > MAX_SCREEN_WIDTH or raw_image.height > MAX_SCREEN_HEIGHT:
            raw_image.thumbnail((MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT))

        self.canvas = tk.Canvas(width=MAX_SCREEN_WIDTH, height=MAX_SCREEN_HEIGHT, bg='white')
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_dragged)
        # canvas = Canvas(width=raw_image.width, height=raw_image.height, bg='white')
        self.canvas.pack()
        self.photo = ImageTk.PhotoImage(raw_image)
        self.image_id = self.canvas.create_image(
            (MAX_SCREEN_WIDTH / 2, MAX_SCREEN_HEIGHT / 2), 
            image=self.photo,
        )

        # TODO: DANGEROUS
        self._last_mouse_x: int = 0
        self._last_mouse_y: int = 0

    def _on_click(self, event):
        print('Detected click at {}, {}'.format(event.x, event.y))
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y

    def _on_dragged(self, event):
        print('Detected drag to {}, {}'.format(event.x, event.y))
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        self.canvas.move(self.image_id, dx, dy)
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y


root = tk.Tk()
app = ImageCropper()
app.mainloop()
