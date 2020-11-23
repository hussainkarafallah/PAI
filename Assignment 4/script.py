import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity
import imutils



def frame_capture(path):
    colored, gray = [], []

    video = cv2.VideoCapture(path)

    while True:
        success, image = video.read()

        if not success:
            break

        colored.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        gray.append(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

    return colored, gray

def save_video(frames, vinfo, output_path):
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(output_path, fourcc, vinfo[2], (int(vinfo[0]), int(vinfo[1])))

    if not out.isOpened():
        raise IOError(f'Could not open or create the file {output_path}')

    for frame in frames:
        out.write(frame)

    out.release()

def process(colored , gray):
    output_frames = []
    L = len(colored)
    DELTA = 8
    for i in range(L - DELTA):

        _, difference = structural_similarity(gray[i + DELTA], gray[i], full=True)
        difference = (difference * 255).astype(np.uint8)

        _, filtered = cv2.threshold(difference, 0, 255, cv2.THRESH_OTSU)
        _, filtered = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY_INV)

        filtered = cv2.morphologyEx(filtered, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours = cv2.findContours(filtered.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        to_show = colored[i].copy()

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)

            x += 5
            w -= 5

            if y < 120 or y > 300 or y + h < 120 or y + h > 300:
                continue

            if w * h < 1000:
                continue

            cv2.rectangle(to_show, (x, y), (x + w, y + h), (0, 0, 255), 2)
        output_frames.append(to_show)
    return output_frames

if __name__ == '__main__':
    colored, gray = frame_capture("./cartracking.mp4")
    output = process(colored , gray)
    print(len(output))
    result = cv2.VideoWriter("./output.mp4", cv2.VideoWriter_fourcc('m', 'p', '4', 'v') , 60 , (684 , 360))
    for frame in output:
        result.write(frame)
    result.release()

