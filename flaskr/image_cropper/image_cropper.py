import sys
import os
import tkinter as tk
from PIL import Image, ImageTk
import json
import pathlib
import enum
import typing 

FEATURED_IMG_SIZE = (1000, 540)
BANNER_SIZE = (1000, 300)
THUMBNAIL_SIZE = (400, 400)

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
    MAX_SCREEN_WIDTH: int = 1000
    MAX_SCREEN_HEIGHT: int = 600
    ANCHOR_SIZE_PX: int = 10
    ANCHOR_COLOR: str = 'blue'

    def __init__(
            self,
            image_path: str,
            desired_width: int,
            desired_height: int,
    ):
        tk.Frame.__init__(self)
        self.master.title('ImageCropper')

        self.image_path = image_path
        self.desired_width = desired_width
        self.desired_height = desired_height

        self.canvas_width = self.MAX_SCREEN_WIDTH
        self.canvas_height = self.MAX_SCREEN_HEIGHT
        self.canvas = tk.Canvas(width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()

        frame = tk.Frame(self, relief=tk.RAISED, borderwidth=1)
        frame.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, expand=True)

        self.cancel_button = tk.Button(self, text='Cancel')
        self.cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.ok_button = tk.Button(self, text='Okay')
        self.ok_button.pack(side=tk.RIGHT)

        # Bindings
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<B1-Motion>', self._on_dragged)
        self.canvas.bind('<KeyPress>', self._on_key_pressed)  # TODO: WHY DOESN'T THIS WORK?
        self.cancel_button.bind('<Button-1>', self._on_cancel_clicked)
        self.ok_button.bind('<Button-1>', self._on_okay_clicked)

        self.raw_image = Image.open(self.image_path)
        self.resized_image = self.raw_image.copy()
        if self.raw_image.width > self.MAX_SCREEN_WIDTH or self.raw_image.height > self.MAX_SCREEN_HEIGHT:
            self.resized_image.thumbnail((self.MAX_SCREEN_WIDTH, self.MAX_SCREEN_HEIGHT))
        self.photo = ImageTk.PhotoImage(self.resized_image)
        self.image_id = self.canvas.create_image(
            (self.MAX_SCREEN_WIDTH / 2, self.MAX_SCREEN_HEIGHT / 2), 
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
                    self.ANCHOR_SIZE_PX, 
                    self.ANCHOR_SIZE_PX,
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
        self.finished_successfully = False
        self.cropped_image = None  # TODO: TYPING

    def _on_click(self, event):
        # print('Detected click at {}, {}'.format(event.x, event.y))
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y
        # Check if user has clicked an anchor
        anchor = self._resolve_anchor(event.x, event.y)
        print('Got anchor {}'.format(anchor))
        # No anchor: check if user is clicking within the image (to drag)
        if anchor == AnchorPosition.NONE:
            if self._are_coords_on_image(event.x, event.y):
                self._is_dragging = True
                self._is_resizing = False
            else:
                self._is_dragging = False  # TODO: THESE ARE MUTUALLY EXCLUSIVE. REPLACE WITH A 'MODE' VARIABLE
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
            print('resizing')
            self._perform_resize(dx, dy, self._resize_anchor)
        self._last_mouse_x = event.x 
        self._last_mouse_y = event.y
        self._update_anchors()
        # Bring the `box` to the top layer
        self.canvas.tag_raise(self.box_id)
        # Move the image to the bottom layer
        self.canvas.tag_lower(self.image_id)

    def _on_key_pressed(self, event):
        print('Detected key press of {}'.format(event.char))

    def _on_cancel_clicked(self, event):
        self.finished_successfully = False
        self.master.destroy()

    def _on_okay_clicked(self, event):
        # Create blank image with the desired dimensions
        self.cropped_image = \
            Image.new('RGB', (self.desired_width, self.desired_height), (255, 255, 255))

        # Calculate top-left of resized image
        img_center_x, img_center_y = self.canvas.coords(self.image_id)
        img_width, img_height = self.photo.width(), self.photo.height()
        img_top_left_x = img_center_x - img_width / 2
        img_top_left_y = img_center_y - img_height / 2

        # Calculate top-left of bounding box
        box_top_left_x = self.canvas_width / 2 - self.desired_width / 2
        box_top_left_y = self.canvas_height / 2 - self.desired_height / 2
            
        # Calculate overlap of resized image and bounding box
        # https://math.stackexchange.com/a/2477358
        overlap_left_x = max(img_top_left_x, box_top_left_x)
        overlap_right_x = min(img_top_left_x + img_width, box_top_left_x + self.desired_width)
        overlap_top_y = max(img_top_left_y, box_top_left_y)
        overlap_bottom_y = min(img_top_left_y + img_height, box_top_left_y + self.desired_height)

        # Found intersect: copy whatever is within the bounding box into `resized_image`
        if overlap_left_x < overlap_right_x and overlap_top_y < overlap_bottom_y:        
            intersect = (overlap_left_x, overlap_top_y, overlap_right_x, overlap_bottom_y)
            print('intersect (absolute coordinates: {}'.format(intersect))
            # Get itersect bounds relative to `resized_image`'s coordinate space
            crop_rel_x1 = overlap_left_x - img_top_left_x
            crop_rel_y1 = overlap_top_y - img_top_left_y
            crop_rel_x2 = crop_rel_x1 + (overlap_right_x - overlap_left_x)
            crop_rel_y2 = crop_rel_y1 + (overlap_bottom_y - overlap_top_y)
            
            # Copy the part of `resized_image` that is within the bounding box
            rel_intersect = (crop_rel_x1, crop_rel_y1, crop_rel_x2, crop_rel_y2)
            cropped_region = self.resized_image.crop(rel_intersect)
            
            # Calculate cropped region relative to top-left of bounding box
            intersect_offset_x1 = int(overlap_left_x - box_top_left_x)
            intersect_offset_y1 = int(overlap_top_y - box_top_left_y)
            # intersect_offset_w = int(crop_rel_x2 - crop_rel_x1)
            # intersect_offset_h = int(crop_rel_y2 - crop_rel_y1)
            # intersect_offset_rect = \
            #     (intersect_offset_x1, intersect_offset_y1, intersect_offset_w, intersect_offset_h)
            # print(intersect_offset_rect)
            self.cropped_image.paste(
                cropped_region, 
                (intersect_offset_x1, intersect_offset_y1)
            )
        # No intersect: leave `resized_image` blank
        else:
            print('no intersect')
        self.finished_successfully = True
        self.master.destroy()

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
        # Iterate through anchor locations and check whether the specified
        # coordinates are in the bounds of one of them. O(n).
        # Note: the "hitboxes" of the anchors are larger than the anchors
        # themselves, to make it easier for the user to click them.
        anchor_positions = self._calc_anchor_positions()
        for anchor, coords in anchor_positions.items():
            if abs(x - coords[0]) < self.ANCHOR_SIZE_PX * 2 and \
                    abs(y - coords[1]) < self.ANCHOR_SIZE_PX * 2:
                return anchor
        return AnchorPosition.NONE

    def _perform_resize(
            self, 
            dx: int, 
            dy: int, 
            anchor: AnchorPosition,
    ):
        img_center_x, img_center_y = self.canvas.coords(self.image_id)
        img_width, img_height = self.photo.width(), self.photo.height()

        if anchor == AnchorPosition.LEFT:
            resized_width = img_width - dx
            resized_height = img_height
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y
        elif anchor == AnchorPosition.BOTTOM_LEFT:
            resized_width = img_width - dx
            resized_height = img_height + dy
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y + dy / 2
        elif anchor == AnchorPosition.BOTTOM_MIDDLE:
            resized_width = img_width
            resized_height = img_height + dy
            new_center_x = img_center_x
            new_center_y = img_center_y + dy / 2
        elif anchor == AnchorPosition.BOTTOM_RIGHT:
            resized_width = img_width + dx
            resized_height = img_height + dy
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y + dy / 2
        elif anchor == AnchorPosition.RIGHT:
            resized_width = img_width + dx
            resized_height = img_height
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y
        elif anchor == AnchorPosition.TOP_RIGHT:
            resized_width = img_width + dx
            resized_height = img_height - dy
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y + dy / 2
        elif anchor == AnchorPosition.TOP_MIDDLE:
            resized_width = img_width
            resized_height = img_height - dy
            new_center_x = img_center_x
            new_center_y = img_center_y + dy / 2
        elif anchor == AnchorPosition.TOP_LEFT:
            resized_width = img_width - dx
            resized_height = img_height - dy
            new_center_x = img_center_x + dx / 2
            new_center_y = img_center_y + dy / 2
        else:
            raise ValueError('No anchor specified')

        # Re-size the original image
        self.resized_image = self.raw_image.resize((resized_width, resized_height))
        # Delete the old image
        self.canvas.delete(self.image_id)
        # Create a new image
        self.photo = ImageTk.PhotoImage(self.resized_image)
        self.image_id = self.canvas.create_image(
            (new_center_x, new_center_y), 
            image=self.photo,
        )


    def _update_anchors(self):
        """Calculates anchor positions and moves anchors to them."""
        anchor_positions = self._calc_anchor_positions()
        for anchor, coords in anchor_positions.items():
            # Get current location of that anchor
            curr_pos = self.canvas.coords(self.anchor_ids[anchor])
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
            img_center_x - img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_LEFT] = (
            img_center_x - img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y + img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_MIDDLE] = (
            img_center_x - self.ANCHOR_SIZE_PX / 2,
            img_center_y + img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.BOTTOM_RIGHT] = (
            img_center_x + img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y + img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.RIGHT] = (
            img_center_x + img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.TOP_RIGHT] = (
            img_center_x + img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y - img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.TOP_MIDDLE] = (
            img_center_x - self.ANCHOR_SIZE_PX / 2,
            img_center_y - img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        anchor_positions[AnchorPosition.TOP_LEFT] = (
            img_center_x - img_width / 2 - self.ANCHOR_SIZE_PX / 2,
            img_center_y - img_height / 2 - self.ANCHOR_SIZE_PX / 2
        )
        return anchor_positions

if __name__ == '__main__':
    execution_path = pathlib.Path(os.getcwd())

    # Look for 'post-meta.json' in the executing directory
    meta_path = execution_path / 'post-meta.json'
    if not meta_path.is_file():
        print('Couldn\'t find "post-meta.json" file in the execution directory')
        sys.exit(1)
    # Read the metadata file
    try:
        with open(meta_path, 'r') as meta_file:
            post_data = json.load(meta_file)
    except IOError:
        print ('ERROR: Could not read the meta-data file ("{}")'.format(meta_path))
        sys.exit(1)

    root = tk.Tk()
    
    from tkinter.filedialog import askopenfilename
    # Ask user to select an image for use
    img_path = askopenfilename(
        initialdir=execution_path,
        title = 'Select image',
        filetypes = (('jpeg files','*.jpg'), ('png files', '*.png'), ('gif files', '*.gif')),
    )
    # Exit if user did not select an image
    if not img_path:
        print('No image selected')
        sys.exit(1)

    img_path = pathlib.Path(img_path)

    # Create featured image
    app = ImageCropper(img_path, FEATURED_IMG_SIZE[0], FEATURED_IMG_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        featured_img = app.cropped_image
    else:
        print('Operation cancelled')
        sys.exit(1)
    
    # Create thumbnail
    app = ImageCropper(str(img_path), THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        thumbnail_img = app.cropped_image
    else:
        print('Operation cancelled')
        sys.exit(1)

    # Create banner
    app = ImageCropper(img_path, BANNER_SIZE[0], BANNER_SIZE[1])
    app.mainloop()
    if app.finished_successfully:
        banner_img = app.cropped_image
    else:
        print('Operation cancelled')
        sys.exit(1)

    # Create the paths for the newly-cropped images
    thumbnail_path = img_path.parent / (img_path.stem + '-thumb.jpg')
    featured_path = img_path.parent / (img_path.stem + '-featured.jpg')
    banner_path = img_path.parent / (img_path.stem + '-banner.jpg')

    # Save images
    thumbnail_img.save(thumbnail_path)
    featured_img.save(featured_path)
    banner_img.save(banner_path)

    # Write image paths to the 'post-meta.json' file, overwriting
    # any paths that are currently there
    post_data['image'] = featured_path.name
    post_data['thumbnail'] = thumbnail_path.name
    post_data['banner'] = banner_path.name
    
    # Write out the updated post metadata
    try:
        with open(meta_path, 'w') as meta_file:
            json.dump(post_data, meta_file, indent=4)
            print('Saved images and updated "post-meta.json" successfully')
    except IOError:
        print ('ERROR: Could not read the meta-data file ("{}")'.format(meta_path))
        sys.exit(1)