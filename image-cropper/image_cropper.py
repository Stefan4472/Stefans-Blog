import tkinter as tk
from PIL import Image, ImageTk
import enum
import typing 

MAX_SCREEN_WIDTH: int = 1000
MAX_SCREEN_HEIGHT: int = 600
ANCHOR_SIZE_PIX: int = 10
ANCHOR_COLOR: str = 'blue'
# REQD_FEATURED_SIZE = (1500, 810)
# REQD_WIDE_BANNER_SIZE = (1900, 300)
# REQD_BANNER_NARROW_SIZE = 


class AnchorPosition(enum.Enum):
    NONE = 0
    LEFT = 1
    BOTTOM_LEFT = 2
    BOTTOM_MIDDLE = 3
    BOTTOM_RIGHT = 4
    RIGHT = 5
    TOP_RIGHT = 6
    TOP_MIDDLE = 7
    TOP_LEFT = 8


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

        self.raw_image = Image.open(self.image_path)
        self.resized_image = self.raw_image.copy()
        if self.raw_image.width > MAX_SCREEN_WIDTH or self.raw_image.height > MAX_SCREEN_HEIGHT:
            self.resized_image.thumbnail((MAX_SCREEN_WIDTH, MAX_SCREEN_HEIGHT))
        self.photo = ImageTk.PhotoImage(self.resized_image)
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

        # Anchor circles, indexed by `AnchorPosition` value
        self.anchor_ids: typing.Dict[AnchorPosition, int] = {}
        for anchor_type in AnchorPosition:
            if anchor_type != AnchorPosition.NONE:
                self.anchor_ids[anchor_type] = self.canvas.create_oval(
                    0, 
                    0, 
                    ANCHOR_SIZE_PIX, 
                    ANCHOR_SIZE_PIX,
                    outline='blue',
                    width=2.0,
                    fill='blue'
                )
        # TODO: DANGEROUS
        self._last_mouse_x: int = 0
        self._last_mouse_y: int = 0
        self._is_dragging: bool = False  # TODO
        self._is_resizing: bool = True
        self._resize_anchor: AnchorPosition = AnchorPosition.NONE
        self._update_anchors()

    def _on_click(self, event):
        # print('Detected click at {}, {}'.format(event.x, event.y))
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y
        # Check if user has clicked on the image
        if self._are_coords_on_image(event.x, event.y):
            print('Within image')
            # Check if user has clicked an anchor
            anchor = self._resolve_anchor(event.x, event.y)
            print('Got anchor {}'.format(anchor))
            # No anchor: set dragging to True
            if anchor == AnchorPosition.NONE:
                self._is_dragging = True
                self._is_resizing = False
            # Anchor: set resizing to True and mark the selected anchor
            else:
                self._is_resizing = True
                self._resize_anchor = anchor
                self._is_dragging = False

    def _on_dragged(self, event):
        # print('Detected drag to {}, {}'.format(event.x, event.y))
        dx = event.x - self._last_mouse_x
        dy = event.y - self._last_mouse_y
        # if self._is_selected:
        if self._is_dragging:
            self.canvas.move(self.image_id, dx, dy)
        elif self._is_resizing:
            self._perform_resize(dx, dy, self._resize_anchor)
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y
        self._update_anchors()

    def _on_key_pressed(self, event):
        print('Detected key press of {}'.format(event.char))

    def _are_coords_on_image(self, x: int, y: int) -> bool:
        """Return whether (x, y) are within the image."""
        img_center_x, img_center_y = self.canvas.coords(self.image_id)
        img_width = self.photo.width()
        img_height = self.photo.height()

        img_top_left_x = img_center_x - img_width / 2
        img_top_left_y = img_center_y - img_height / 2

        return \
            x >= img_top_left_x and x <= img_top_left_x + img_width and \
            y >= img_top_left_y and y <= img_top_left_y + img_height

    def _resolve_anchor(self, x: int, y: int) -> AnchorPosition:
        # img_center_x, img_center_y = self.canvas.coords(self.image_id)
        # img_width = self.photo.width()
        # img_height = self.photo.height()
        # img_top_left_x = img_center_x - img_width / 2
        # img_top_left_y = img_center_y - img_height / 2

        # check_left_anchor = \
        #     x >= img_top_left_x and x <= img_top_left_x + img_width * 0.1
        # check_right_anchor = \
        #     x >= img_top_left_x + img_width * 0.9 and x <= img_top_left_x + img_width
        # check_top_anchor = \
        #     y >= img_top_left_y and y <= img_top_left_y + img_height * 0.1
        # check_bottom_anchor = \
        #     y >= img_top_left_y + img_height * 0.9 and y <= img_top_left_y + img_height

        # if check_left_anchor:
        #     return AnchorPosition.FROM_LEFT
        # elif check_right_anchor:
        #     return AnchorPosition.FROM_RIGHT
        # elif check_top_anchor:
        #     return AnchorPosition.FROM_TOP
        # elif check_bottom_anchor:
        #     return AnchorPosition.FROM_BOTTOM
        # else:
        #     return AnchorPosition.NONE
        return AnchorPosition.NONE

    def _perform_resize(self, dx: int, dy: int, anchor: AnchorPosition):
        # img_center_x, img_center_y = self.canvas.coords(self.image_id)
        # img_width = self.photo.width()
        # img_height = self.photo.height()
        # img_top_left_x = img_center_x - img_width / 2
        # img_top_left_y = img_center_y - img_height / 2

        # resized_width = img_width + dx
        # resized_height = img_height + dy
        # print('should resize to {}, {}'.format(resized_width, resized_height))

        # if anchor == AnchorPosition.FROM_LEFT:
        #     new_center_x = img_center_x + dx / 2
        #     new_center_y = img_center_y
        # elif anchor == AnchorPosition.FROM_RIGHT:
        #     new_center_x = img_center_x - dx / 2
        #     new_center_y = img_center_y
        # elif anchor == AnchorPosition.FROM_TOP:
        #     new_center_x = img_center_x
        #     new_center_y = img_center_y + dy / 2
        # elif anchor == AnchorPosition.FROM_BOTTOM:
        #     new_center_x = img_center_x
        #     new_center_y = img_center_y - dy / 2
        # else:
        #     raise ValueError('Invalid anchor {}'.format(anchor))

        # # Re-size the original image
        # self.resized_image = self.raw_image.resize((resized_width, resized_height))
        # # Delete the old image
        # self.canvas.delete(self.image_id)
        # # Create a new image
        # self.photo = ImageTk.PhotoImage(self.resized_image)
        # self.image_id = self.canvas.create_image(
        #     (new_center_x, new_center_y), 
        #     image=self.photo,
        # )
        return

    def _update_anchors(self):
        """Calculates anchor positions and moves anchors to them."""
        anchor_positions = self._calc_anchor_positions()
        for anchor, coords in anchor_positions.items():
            # Get current location of that anchor
            curr_pos = self.canvas.coords(self.anchor_ids[anchor])
            print(curr_pos)
            # Calculate displacement required
            dx = coords[0] - curr_pos[0]
            dy = coords[1] - curr_pos[1]
            self.canvas.move(self.anchor_ids[anchor], dx, dy)

    def _calc_anchor_positions(
            self,
    ) -> typing.Dict[AnchorPosition, typing.Tuple[int, int]]:
        """Based on the current image, calculates where the anchors are."""
        img_center_x, img_center_y = self.canvas.coords(self.image_id)
        img_width, img_height = self.photo.width(), self.photo.height()

        anchor_positions = {}
        anchor_positions[AnchorPosition.LEFT] = (
            img_center_x - img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_LEFT] = (
            img_center_x - img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y + img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_MIDDLE] = (
            img_center_x - ANCHOR_SIZE_PIX / 2,
            img_center_y + img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_RIGHT] = (
            img_center_x + img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y + img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.RIGHT] = (
            img_center_x + img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.TOP_RIGHT] = (
            img_center_x + img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y - img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.TOP_MIDDLE] = (
            img_center_x - ANCHOR_SIZE_PIX / 2,
            img_center_y - img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        anchor_positions[AnchorPosition.TOP_LEFT] = (
            img_center_x - img_width / 2 - ANCHOR_SIZE_PIX / 2,
            img_center_y - img_height / 2 - ANCHOR_SIZE_PIX / 2
        )
        return anchor_positions

# ... user chooses file from directory
img_path: str = 'cpp_game_screenshot_2.jpg'

root = tk.Tk()
app = ImageCropper(img_path, 400, 400)
app.mainloop()

# finally ... overwrite json file?