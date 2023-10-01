import cv2 as cv
import math as m
import pandas as pd
from skimage.metrics import structural_similarity

max_v_pixels_per_frame = 12

# Measurd 252 pixels to cover a 41cm wide cement block in the background
pixel_per_cm = 252 / 41
pixel_per_m = pixel_per_cm * 100

infile = '/home/jbuist/git/phy230/ballshot/trimmed/incline5.mp4'
outfile = infile.replace('mp4', 'csv')
pngfile = infile.replace('mp4', 'png')

# With videos trimmed we'll just use the first frame as reference
skip_frames = 1


def output_data(screen_positions, screen_timestamps):
    p1 = screen_positions[0]
    out_df = pd.DataFrame(
        columns=['screenx', 'screeny',
                 'ms', 'seconds',
                 'xpos', 'ypos',
                 ]
    )
    out_df.ms = screen_timestamps
    out_df.seconds = [ms/1000 for ms in screen_timestamps]
    out_df.screenx = [p[0] for p in screen_positions]
    out_df.screeny = [p[1] for p in screen_positions]
    out_df.screenx -= p1[0]
    out_df.screeny -= p1[1]
    out_df.screenx *= -1.0
    out_df.screeny *= -1.0
    out_df.xpos = out_df.screenx / pixel_per_m
    out_df.ypos = out_df.screeny / pixel_per_m
    out_df.to_csv(outfile)


def main():
    video = cv.VideoCapture(filename=infile)
    last_frame = None
    min_x, max_x = 175, 1220
    min_y, max_y = 30, 350
    bbox = (min_x, min_y, max_x-min_x, max_y-min_y)
    for x in range(skip_frames):
        _, orig_frame = video.read()

    orig_frame = cv.cvtColor(orig_frame, cv.COLOR_BGR2GRAY)
    last_known_pos = [None, None]
    sphere_screen_pos = []
    sphere_timestamps = []
    frame_count = 0
    begin_ts = None
    while True:
        ret, image = video.read()
        if ret is None or image is None:
            break  # End of video file
        if begin_ts is None:
            ms = video.get(cv.CAP_PROP_POS_MSEC) / 8
            begin_ts = ms
            print(ms)
        frame_count += 1
        # print(f'Frame: {frame_count}')
        ms = video.get(cv.CAP_PROP_POS_MSEC) / 8
        video_ts = ms-begin_ts
        curr_frame = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # cv.imshow('Video', frame)
        if last_frame is not None:
            (score, diff) = structural_similarity(orig_frame, curr_frame,
                                                  full=True)
            diff = (diff * 255).astype("uint8")
            ret, thresh = cv.threshold(diff, 127, 255, 0)
            contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE,
                                                  cv.CHAIN_APPROX_SIMPLE)
            good_contours = []
            bad_contours = []
            for c in contours:
                M = cv.moments(c)
                area = M["m00"]
                if area > 900000:  # What is this thing!?
                    continue
                if area < 100:
                    continue
                cX = int(M["m10"] / area)
                cY = int(M["m01"] / area)
                pos = [cX, cY]
                # Check if the center of maxx is within our search box
                if cX >= min_x and cX <= max_x and cY >= min_y and cY <= max_y:
                    approx = cv.approxPolyDP(c, 0.01*cv.arcLength(c, True),
                                             True)
                    if None not in last_known_pos:
                        dist = m.dist(last_known_pos, pos)
                    else:
                        dist = max_v_pixels_per_frame + 1

                    if ((len(approx) > 8 and len(approx) < 21)
                        or
                       (dist <= max_v_pixels_per_frame)):
                        good_contours.append(c)
                        sphere_screen_pos.append(pos)
                        sphere_timestamps.append(video_ts)
                        cv.circle(image, (cX, cY), 10, (255, 0, 255), -1)
                    else:
                        bad_contours.append(c)

            if len(good_contours) == 1:
                last_known_pos = [cX, cY]
            # cv.drawContours(image, good_contours, -1, (0, 255, 0), 3)
            cv.drawContours(image, bad_contours, -1, (0, 0, 255), 3)
            for pos in sphere_screen_pos:
                cv.circle(image, pos, 5, (255, 0, 000), 2)

            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv.rectangle(image, p1, p2, (0, 255, 0), 10)
            cv.imshow('diff', image)
            last_image = image.copy()
            # cv.imwrite('test.png', image)
        last_frame = curr_frame.copy()
        if not ret:
            break
        if cv.waitKey(1) == ord('q'):
            break
    cv.imwrite(pngfile, last_image)
    output_data(sphere_screen_pos, sphere_timestamps)
    video.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
