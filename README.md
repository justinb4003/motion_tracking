# Motion Tracking with Python

Here's a fun little play thing that tracks motion of an object within a video
frame.

It does not have any user interface to it. You'll have o edit the source code
between runs to et any options like the location of the bounding box that it
looks for action in, the number of frames to skip before processing anything,
and the input file.

The output is a CSV of the location of your object in screen and real life
coordinates. The PNG shows the last processed frame of the video. You can quit
an analysis early by pressing 'q' on your keyboard if the video runs too long
and you want to ignore the later data results. The blue dots are the locations
here the object was detected. The pink blob is the current/final location of
it. The green box around a section of the screen indicates the area we want to
pay attention to and is controled by `min_x`, `max_x`, `min_y`, and `max_y`
in the code.


## Install / Running

You'll need a functional Python installation to start with. Check with
http://python.org if you need to install it. Once that's done you'll want to
clone the repository, create a virtual environment, and then install the
packages in `requirements.txt` with `pip -r requirements.txt` though you _can_
instll the package globally with just the last `pip` command.


Once you're ready to go edit `track.py` to set the proper location for your
video file and run it with `python track.py`. If you press 'q' while running or
it reches the end of the file the output of the tracked points will be output
to a CSV file in the same didrectory with the same name but a `.csv` extension.
There will also be a `.png` file there that shows the last proessed video frame.