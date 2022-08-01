In the [previous post](/post/gamedev-computer-graphics) we created a computer animation of a bouncing square. In this post we'll use Java to implement a Spritesheet class, with which we can play back hand-drawn animation sequences.

A spritesheet lays out the frames of an animation, like a film roll from one of those old-time movies. The frames are lined up back to back (left to right) and composed into a single image. Each frame has the same width and height. You can think of it as taking a flip book, peeling apart the individual stickies, and laying them out from left to right.

*(By the way: For a cool blog about animation, check out [Pedro Medeiros on Patreon](https://www.patreon.com/saint11))*

I found this [public domain spritesheet](https://openclipart.org/detail/248259/retro-character-sprite-sheet), which we'll use for our example.  

<x-image>
	<path>walking_spritesheet.png</path>
</x-image>


Note that there are four separate animations in that one image--each row is a four-frame loop drawn from a different perspective (front, back, left, right). We're going to just take the top row.

<x-image>
	<path>walking_front.png</path>
</x-image>

Let's write a class that'll provide Spritesheet functionality. We'll give it our whole spritesheet image, tell it how many frames are in the image, and then be able to play the frames back one by one. ([See the full code here](https://github.com/Stefan4472/Blog-ExampleCode/tree/master/gamedev-from-scratch/3-spritesheets/simple-spritesheet))

<x-code language="java">
import java.awt.image.BufferedImage;

// Spritesheet that loops and displays each frame once
public class Spritesheet {

    private int counter = -1;       // current frame we're on (0-indexed)
    private int frameWidth, frameHeight;   // width and height of each frame (px)
    private int numFrames;          // number of frames in the sequence
    private BufferedImage img;      // the image itself

    // initialize with image and the number of frames it contains
    public Spritesheet(BufferedImage img, int numFrames) {
        this.img = img;
        frameWidth = img.getWidth() / numFrames;  // calculate width of each frame (px)
        frameHeight = img.getHeight();
        this.numFrames = numFrames;
    }

    // return the next frame in the sequence
    public BufferedImage next() {
        // increment counter. Use modulus to ensure it remains within the bounds of numFrames
        counter = (counter + 1) % numFrames;
        // return subimage containing the specified frame
        return img.getSubimage(counter * frameWidth, 0, frameWidth, frameHeight);  
    }

    public int getFrameWidth() {
        return frameWidth;
    }

    public int getFrameHeight() {
        return frameHeight;
    }
}
</x-code>

The class has a very simple interface: all we need to do is call ```next()``` to get the next frame in the sequence. Each frame is displayed once, and the sequence loops once we get to the end.

To demonstrate what this looks like in action, let's write a JFrame class to play back the frames of the animation. We'll be using a few Swing GUI commands you may be unfamiliar with. The most important part is the ActionListener we create, which basically tells the screen to redraw itself every 33 milliseconds.

<x-code language="java">
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

// Shows JFrame window where spritesheet animation plays at 30FPS
public class SpritesheetDemo extends JFrame {

    private static final int DELAY = 200;  // number of ms delay between frames (set to 200 for demo purposes)
    private Spritesheet spritesheet;     // spritesheet to display
    private int windowWidth, windowHeight;

    public SpritesheetDemo(Spritesheet spritesheet) {
        this.spritesheet = spritesheet;
        windowWidth = spritesheet.getFrameWidth();
        windowHeight = spritesheet.getFrameHeight() + 30;
        // set window size to spritesheet frame size
        setSize(new Dimension(windowWidth, windowHeight));
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        setTitle("Spritesheet Display");
        setVisible(true);

        // set up an ActionListener to invalidate and redraw the window every DELAY milliseconds
        ActionListener taskPerformer = new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                repaint();  // repaint the screen
            }
        };
        new Timer(DELAY, taskPerformer).start();
    }

    // Clear the window and draw the spritesheet's next frame
    public void paint(Graphics g) {
        g.setColor(Color.WHITE);  // set color to white
        g.fillRect(0, 0, windowWidth, windowHeight); // reset the window by drawing over it with white
        ((Graphics2D) g).drawImage(spritesheet.next(), null, 0, 30);
    }
}
</x-code>

If we create a Main class, we can then run SpritesheetDemo.

<x-code language="java">
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class Main {

    public static void main(String[] args) {
		// create Spritesheet using spritesheet_move.png image. tell the constructor the image has 4 frames.
        Spritesheet spritesheet = new Spritesheet(loadImage("walking_front.png"), 4);
        SpritesheetDemo demo = new SpritesheetDemo(spritesheet);

    }

    // utility method that reads an image file into memory given the file path. Returns BufferedImage.
    // raises IOException if file cannot be found
    public static BufferedImage loadImage(String path) throws IllegalArgumentException {
        try {
            return ImageIO.read(new File(path));
        } catch (IOException e) {
            throw new IllegalArgumentException("Could not find or read the file \'" + path + "\'"); // todo: use format
        }
    }
}
</x-code>

<x-image>
	<path>spritesheet_demo1.gif</path>
	<caption>Each frame is being shown for 200 milliseconds.</caption>
</x-image>

In practice though, our Spritesheet class is too simple. It would be great if we could define how long each frame should be displayed, i.e. how many times we could call ```next()``` and get the same frame. For example, we could show frames 1-3 one time each, then frame 4 five times, and frame 5 seven times. Then we could precisely control the timing of the animation.

In the Spritesheet constructor, we'll change the ```numFrames``` parameter to ```int[] frameCounts```, an array defining the number of times to show each frame in the animation. We're also going to replace ```counter``` with ```int frameIndex```, which will keep track of which frame we're on in the series, and ```int subIndex```, which will keep track of how many times we've shown the current frame.

Our ```next()``` method will look a little different: first we're going to increment subIndex. Then, we'll check if subIndex is equal to the number of times we wanted to show the frame at ```frameIndex```--in this case, we need to move on to the next frame in the series. ([See the full code here](https://github.com/Stefan4472/Blog-ExampleCode/tree/master/gamedev-from-scratch/3-spritesheets/timed-spritesheet))

<x-code language="java">
import java.awt.image.BufferedImage;

// A spritesheet that can show sub-frames for varying lengths
public class Spritesheet {

    private int frameIndex = 0;
    private int subIndex = -1;
    private int[] frameCounts;
    private int width, height;
    private BufferedImage img;

    // initialize with an image and an array of frame durations
    public Spritesheet(BufferedImage img, int[] frameCounts) {
        this.img = img;
        this.frameCounts = frameCounts;
        width = img.getWidth() / frameCounts.length;  // calculate pixel width of each sub-frame
        height = img.getHeight();
    }

    // return the next frame from the sequence
    public BufferedImage next() {
        subIndex++;
        if (frameCounts[frameIndex] == subIndex) {
            subIndex = 0;
            frameIndex = (frameIndex + 1) % frameCounts.length;
        }
        return img.getSubimage(frameIndex * width, 0, width, height);  // return ensuing subimage
    }

    // return width of each frame in the spritesheet (px)
    public int getFrameWidth() {
        return width;
    }

    // return height of each frame in the spritesheet (px)
    public int getFrameHeight() {
        return height;
    }
}
</x-code>

We'll also need to modify ```main()``` to provide the frameCounts.

<x-code language="java">
public static void main(String[] args) {
    int[] frame_counts = { 4, 6, 10, 3 };
    Spritesheet spritesheet = new Spritesheet(loadImage("walking_front.png"), frame_counts);
    SpritesheetDemo demo = new SpritesheetDemo(spritesheet);
}
</x-code>

<x-image>
	<path>spritesheet_demo2.gif</path>
	<caption>Pardon the flickering... I think there's a problem with my graphics card.</caption>
</x-image>

That's all I'll be showing in this tutorial, but here's a small list of features you could implement that I've found very useful in the past:
- Turn looping on/off. If looping is off, and the animation is on its last frame, calling ```next()``` should throw an exception (e.g. IndexOutOfBoundsException)
- If looping can be turend off, you'll need a ```hasNext()``` method that returns whether calling ```next()``` is allowed. This would be true until the last frame of the animation.
- A ```restart()``` method that goes back to the first frame.
- A ```hasPlayed()``` method that returns True if the animation has played through at least once.

Read on in [Sprites](/post/gamedev-sprites), Part 4 of the Series.