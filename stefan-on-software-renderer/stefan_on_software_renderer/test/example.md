In the [previous post](/post/gamedev-computer-graphics) we talked about how images and graphics are stored on a computer. In this post we'll explain how computer animation works, and create one of our own using Java.

First things first: an animation is a sequence of images that are played back so fast your brain blends them into a single, cohesive motion.

Animation is in fact an illusion. Think of the film strips that were used in the early days of cinema, or the flip books you may have seen as a kid. Those are a bunch of images that get shown to you so briefly, it feels like you're watching a video.

<x-image>
	<path>vintage-film-reel.jpg</path>
	<caption>Photo of a hand-colored reel from a 1989 film called "Little Nemo: Adventures in Slumberland" ([source](https://upload.wikimedia.org/wikipedia/commons/3/34/Little_Nemo_film_-_hand-colored_filmreel.jpg))</caption>
</x-image>

To trick your viewer into seeing fluid, realistic motion, you need to show 25-30 still images per second, with small changes made between each frame. Each image is called a _frame_, and we say _"Frames per Second"_ to indicate how many frames are played back per second.

_Creating_ animation is hard, because you need to draw each one of those frames manually. You can either draw them digitally yourself (covered in the spritesheets tutorial), or write a program to generate the frames for you. We'll be doing the latter today, with a program that animates a square moving across the screen.

We'll be using Java Swing, which is a library for writing GUIs. We'll be using the simplest setup possible--a single window, called a JFrame, which we'll draw our animations on. ([See the full code here](https://github.com/Stefan4472/Blog-ExampleCode/tree/master/gamedev-from-scratch/2-animation/draw-square/src))

<x-code language="java">
import javax.swing.*;
import java.awt.*;

// Creates a JFrame window and draws a Blue square to it
public class DrawSquare extends JFrame {

    // custom RGB-color used to draw the square
    private static final Color BLUE = new Color(66, 122, 244);
    // dimensions of window (px)
    private static final int SCREEN_W = 300, SCREEN_H = 300;

    // constructor initializes the JFrame and sets it to display
    public DrawSquare() {
        setSize(new Dimension(SCREEN_W, SCREEN_H));  // set size of window to SCREEN_W * SCREEN_H pixels
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);  // exit program on window close
        setTitle("Animation Example");  // set window title
        setVisible(true);  // show the window
    }

    @Override // code to draw (paint) the window square to the canvas. Called when the window is displayed.
    // Will not be called again unless the window has to be redrawn.
    public void paint(Graphics g) {
        g.setColor(BLUE);  // set color to be used for drawing calls
        g.fillRect(50, 50, 50, 50);  // draw square with top-left coordinate at (50, 50) and width/height of 50 px
    }
}
</x-code>

In this code the DrawSquare class is an extended JFrame, so we're basically just modifying a few features from the standard JFrame window class. We set the size to constants we defined (`SCREEN_W` and `SCREEN_H`), do some other GUI setup, and override the `paint()` method, which specifies how to draw the window.

This is where all our drawing code goes. As you can see, our code simply draws a filled rectangle at coordinates (50, 50) with width and height of 50 pixels.

Now let's add a very simple main class to show the window:
<x-code language="java">
public class Main {
    public static void main(String[] args) {
        new DrawSquare();
    }
}
</x-code>

If we compile the code and run Main, we'll see the following screen:

<x-image>
	<path>example-draw-square.jpg</path>
</x-image>

But animation is all about movement, and our square doesn't move.

How do we create smooth movement? As explained above, we create a bunch of frames, with a tiny change each time.

Let's add code that will trigger the screen to redraw every 33 milliseconds (~30 FPS), and each time the screen redraws, let's draw the square a few pixels to the right. ([See the full code here](https://github.com/Stefan4472/Blog-ExampleCode/tree/master/gamedev-from-scratch/2-animation/draw-moving-square/src))

<x-code language="java">
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

// Creates a JFrame window and animates a blue square moving across it
public class DrawMovingSquare extends JFrame {

    // custom RGB-color used to draw the square
    private static final Color GREEN = new Color(39, 100, 42);
    // dimensions of window (px)
    private static final int SCREEN_W = 300, SCREEN_H = 300;
    // number of ms to delay between redrawing the window
    private static final int DELAY = 33;
    // top-left x-coordinate of square
    private int square_x = 40;  

    // constructor initializes the JFrame and sets it to display
    public DrawMovingSquare() {
        setSize(new Dimension(SCREEN_W, SCREEN_H));  // set size of window to SCREEN_W x SCREEN_H pixels
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);  // exit program on window close
        setTitle("Animation Example");  // set screen title
        setVisible(true);  // show the window

        // create a timer to redraw the window every DELAY milliseconds. This uses an ActionListener
        // that will call actionPerformed() repeatedly. Inside actionPerformed we update animation logic,
        // then repaint the window. We could put more updating logic in this method if we wanted to.
        Timer timer = new Timer(DELAY, new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                update();  // update position of square
                repaint();  // repaint the screen
            }
        });
        // start the timer
        timer.start();  
    }

    // updates the square's position between frames, adding 5 to the square's coordinate each call
    public void update() {
        square_x += 5;
    }

    @Override // code to draw (paint) the window
    public void paint(Graphics g) {
        g.setColor(Color.WHITE);  // set color to white
        g.fillRect(0, 0, SCREEN_W, SCREEN_H); // reset the window by drawing over it with white
        g.setColor(Color.BLUE);  // set color to blue
        g.fillRect(square_x, 50, 50, 50);  // draw square with correct coordinate and width/height of 50 px
    }
}
</x-code>

We use the Timer to trigger regular, repeated calls to `update()` and `paint()`. In `update()`, we add 5 to the square's last coordinate (stored in the `square_x` variable). In `paint()`, we fill the entire window with white (as a way to reset the screen from the last frame) and draw the square at its new location. This way, as we run `update()` and `paint()` 30 times a second, the square moves fluidly to the right.

We also have to modify `main()` with the new class name ("DrawMovingSquare").
<x-code language="java">
public class Main {
    public static void main(String[] args) {
        new DrawMovingSquare();
    }
}
</x-code>

<x-image>
	<path>example-moving-square.gif</path>
</x-image>

_Good to Know: Performing graphics functions takes time. An important optimization in animation and game development is to only redraw parts of the screen that changed since the last frame. In this case, instead of painting over the entire window with white, we could paint over the square's last position to hide it._

As interesting as that animation is, there's a problem: the square moves to the right, and doesn't stop, trundling happily off the screen edge into oblivion.

The Graphics object/canvas we draw on is in practice infinite (although in reality it does have memory constraints). This means we can draw the square at any coordinate we please, like `(10_000_000, 0)`, and the square will exist somewhere on the canvas, but not in a place we can see. ***Drawing to the wrong coordinates, or coordinates that are off the screen, is a common bug.***

As our last exercise, let's make the square bounce off the screen edges. We'll need to add code to our `update()` method to check the current coordinates each frame, and reverse the square's speed when we hit a screen edge.

We'll add `int square_w` to define the width of the square, and `int speed_x` to keep track of the square's speed in the x-direction.

We'll also add some code to change the square color each frame. To keep it simple, we'll fluctuate between white and black. We'll use one integer (`color_int`) that will cycle gradually from 0 to 255. Each frame, we'll add `color_change` to `color_int`, and set the drawing color's RGB to `(color_int, color_int, color_int)`. We'll reverse `color_change` direction at the bounds (0 and 255). ([See the full code here](https://github.com/Stefan4472/Blog-ExampleCode/tree/master/gamedev-from-scratch/2-animation/draw-changing-square/src))

<x-code language="java">
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

// Creates a JFrame window and animates a square moving across it, bouncing off the window edges.
// The square's color changes over time, varying from white to black and back again.
public class DrawChangingSquare extends JFrame {

    // dimensions of window (px)
    private static final int SCREEN_W = 300, SCREEN_H = 300;
    // number of ms to delay between redrawing the window
    private static final int DELAY = 33;

    private int square_x = 40;  // top-left x-coordinate of square
    private int square_w = 50;  // width of each square edge (px)
    private int speed_x = 5;  // amount to add to square_x each frame
    private int color_int = 0;  // integer to be used in each RGB color channel
    private int color_change = 5;  // amount to add/subtract to color_int each frame (higher = faster change)

    // constructor initializes the JFrame and sets it to display
    public DrawChangingSquare() {
        setSize(new Dimension(SCREEN_W, SCREEN_H));  // set size of window to SCREEN_W x SCREEN_H pixels
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);  // exit program on window close
        setTitle("Animation Example");  // set screen title
        setVisible(true);  // show the window

        // create a timer to redraw the window every DELAY milliseconds. This uses an ActionListener
        // that will call actionPerformed repeatedly. Inside actionPerformed we update animation logic,
        // then repaint the window. More logic could be put into this method if we so wished.
        Timer timer = new Timer(DELAY, new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                update();  // update position of square
                repaint();  // repaint the screen
            }
        });
        timer.start();
    }

    // updates the square's position and color each frame to create animation over time
    public void update() {
        // increment x-coordinate
        square_x += speed_x;

        // check if we've hit the right edge of the canvas
        if (square_x + square_w > SCREEN_W) {
            square_x = SCREEN_W - square_w;  // set to edge
            speed_x *= -1;  // reverse speed
        } else if (square_x < 0) {  // check if we've hit the left edge of the canvas
            square_x = 0;  // set to edge
            speed_x *= -1;  // reverse speed
        }

        // increment color_int
        color_int += color_change;

        // check color bounds (must be from 0-255)
        if (color_int > 255) {
            color_change *= -1;  // reverse color change direction
            color_int = 255;  // set to 255 (upper bound)
        } else if (color_int < 0) {
            color_change *= -1;  // reverse color change direction
            color_int = 0;  // set to 0 (lower bound)
        }
    }

    @Override // code to draw (paint) the window square to the canvas.
    public void paint(Graphics g) {
        g.setColor(Color.WHITE);  // set color to white
        g.fillRect(0, 0, SCREEN_W, SCREEN_H); // reset the window by drawing over it with white
        g.setColor(new Color(255, color_int, color_int));  // set color: all three channels are color_int
        g.fillRect(square_x, 50, square_w, square_w);  // draw square with correct coordinate and width/height
    }
}
</x-code>

Finally, let's update `main()` again.
<x-code language="java">
public class Main {
    public static void main(String[] args) {
        new DrawChangingSquare();
    }
}
</x-code>

<x-image>
	<path>example-changing-square.gif</path>
</x-image>

_Also Good to Know: I recommend working with coordinates and speeds in floats. This way, for especially slow or precise motion, you can support sub-pixel speeds._

There's a lot more we can do with this frame-by-frame style of animation, and the key is to think logically and progress through examples of increasing difficulty. There are a lot of engines and tools that'll abstract the painful details away, but under the hood there's no escaping the frame-by-frame approach.

Personally, I think it's really cool to get your own examples working from scratch. Understanding how it all works is one of the joys of programming.

In the next part [we'll implement and use Spritesheets](/post/gamedev-spritesheets) to display hand-drawn animations.