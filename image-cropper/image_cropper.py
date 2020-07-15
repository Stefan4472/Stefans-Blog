import tkinter as tk
from PIL import Image, ImageTk
import enum

MAX_SCREEN_WIDTH: int = 1000
MAX_SCREEN_HEIGHT: int = 600

# REQD_FEATURED_SIZE = (1500, 810)
# REQD_WIDE_BANNER_SIZE = (1900, 300)
# REQD_BANNER_NARROW_SIZE = 


class AnchorPosition(enum.Enum):
    NONE = 0
    FROM_LEFT = 1
    FROM_RIGHT = 2
    FROM_TOP = 3
    FROM_BOTTOM = 4


class ImageCropper(tk.Frame):
    def __init__(
            self,
            image_path: str,
            desired_width: int,
            desired_height: int,
    ):
        tk.Frame.__init__(self)

        self.image_path = image_path
        self.desired_width = desired_width
        self.desired_height = desired_height

        self.canvas_width = MAX_SCREEN_WIDTH
        self.canvas_height = MAX_SCREEN_HEIGHT
        self.canvas = tk.Canvas(width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_dragged)
        self.bind('<KeyPress>', self._on_key_pressed)  # TODO: WHY DOESN'T THIS WORK?
        self.canvas.pack()

        raw_image = Image.open(self.image_path)
        if raw_image.width > MAX_SCREEN_WIDTH or raw_image.height > MAX_SCREEN_HEIGHT:
            raw_image.thumbnail((MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT))
        self.photo = ImageTk.PhotoImage(raw_image)
        self.image_id = self.canvas.create_image(
            (MAX_SCREEN_WIDTH / 2, MAX_SCREEN_HEIGHT / 2), 
            image=self.photo,
        )

        # Create bounding box, centered in the canvas
        width_diff = self.canvas_width - self.desired_width
        height_diff = self.canvas_height - self.desired_height
        self.box_id = self.canvas.create_rectangle(
            width_diff / 2,   # x1
            height_diff / 2,  # y1
            self.canvas_width - width_diff / 2,  # x2 
            self.canvas_height - height_diff / 2, # y2
            outline='red',
            width=5.0,
        )

        # TODO: DANGEROUS
        self._last_mouse_x: int = 0
        self._last_mouse_y: int = 0
        self._is_dragging: bool = False  # TODO
        self._is_resizing: bool = True
        self._resize_anchor: AnchorPosition = AnchorPosition.NONE

    def _on_click(self, event):
        # print('Detected click at {}, {}'.format(event.x, event.y))
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y
        if self._are_coords_on_image(event.x, event.y):
            print('Within image')

    def _on_dragged(self, event):
        # print('Detected drag to {}, {}'.format(event.x, event.y))
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        # if self._is_selected:
        if self._is_dragging:
            self.canvas.move(self.image_id, dx, dy)
        elif self._is_resizing:
            img_center_x, img_center_y = self.canvas.coords(self.image_id)
            img_top_left = img_center_x - self.photo.width() / 2
            img_top_right = img_center_y - self.photo.height() / 2
            print(img_top_left, img_top_right)
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y

    def _on_key_pressed(self, event):
        print('Detected key press of {}'.format(event.char))

    def _are_coords_on_image(self, x: int, y: int) -> bool:
        """Return whether (x, y) are within the image."""
        img_center_x, img_center_y = self.canvas.coords(self.image_id)
        img_width = self.photo.width()
        img_height = self.photo.height()

        img_top_left_x = img_center_x - img_width / 2
        img_top_left_y = img_center_y - img_height / 2

        is_within = \
            x >= img_top_left_x and x <= img_top_left_x + img_width and \
            y >= img_top_left_y and y <= img_top_left_y + img_height

        return is_within

    def _resolve_anchor(self, x: int, y: int) -> AnchorPosition:
        return AnchorPosition.NONE

# ... user chooses file from directory
img_path: str = 'cpp_game_screenshot_2.jpg'

root = tk.Tk()
app = ImageCropper(img_path, 400, 400)
app.mainloop()

# finally ... overwrite json file?