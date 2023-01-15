# tk-image-cropper

A simple program that uses a Tkinter GUI to display and visually crop an image to the desired width and height. Simply call
```
image_cropper.run_image_cropper(
    img_path: pathlib.Path,
    desired_width: int,
    desired_height: int,
    out: pathlib.Path,
)
```

to crop the image at `img_path` to (`desired_width`, `desired_height`) and write the resulting output file to `out`.