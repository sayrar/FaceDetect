# Import necessary modules
import sys, os, cv2
from PyQt5 import QtCore
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
    QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox, QFrame, QFileDialog, 
    QMessageBox, QHBoxLayout, QVBoxLayout, QAction, QRubberBand)
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QRect
import platform
import glob
import time
import re
from datetime import datetime as dt
from pathlib import Path


if platform.system() == "Windows":
    DATA_FOLDER = "downloads\\"
    SLASH = "\\"
else:
    DATA_FOLDER = "downloads/"
    SLAHS = "/"


style_sheet = """
    QLabel#ImageLabel{
        color: darkgrey;
        border: 2px solid #000000;
        qproperty-alignment: AlignCenter
    }"""


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') # We load the cascade for the face.


class ImageProcessingGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()
    def initializeUI(self):
        """Initialize the window and display its contents to the screen."""

        self.output_file = "session-{}.txt".format(time.time())
        self.id_folders = sorted(glob.glob(DATA_FOLDER + "*"))
        self.current_folder = 0
        self.current_img = 0
        self.step_size = 1
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0         

        files = glob.glob("./*")
        paths = []
        for path in Path(DATA_FOLDER).rglob('*.*'):
            paths.append(path)
        print(len(paths))
        self.checkPreviousSession(files)

        folder = self.id_folders[self.current_folder]
        self.person = folder.split("/")[-1]
        self.image_paths = sorted(glob.glob(folder+"/"+"*"))
        self.current_image = self.image_paths[self.current_img]

        self.setMinimumSize(900, 600)
        self.setWindowTitle('Image Labeling')
        self.setupWindow()
        self.openImage()
        #self.setupMenu()
        self.show()

    def checkPreviousSession(self, files):
        #print(reversed(sorted(files)))
        for path in reversed(sorted(files)):
            prev_session = re.search("(session-(\d+\.\d+)\.txt)",path)
            if prev_session:
                readable_time = dt.fromtimestamp(float(
                              prev_session.group(2))).strftime('%Y-%m-%d %H:%M:%S')
                resume = QMessageBox.question(self, 'Load Session', 'Detected session: ' + readable_time
                                       + '\n\nWould you like to resume this session?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if resume == QMessageBox.Yes:
                    self.output_file = path
                    with open(path) as label_file:
                        last_labeled_person, last_labeled_image = label_file.readlines()[-1].split(":")
                        print(last_labeled_image)
                        print(last_labeled_person)
                        self.current_folder = self.id_folders.index(DATA_FOLDER + last_labeled_person) \
                            + self.step_size -1 
                        folder_list = glob.glob(self.id_folders[self.current_folder])
                        print(folder_list)
                        self.currerent_img = self.id_folders.index(folder_list + "/" + last_labeled_image)
                break

    def setupWindow(self):
        """Set up widgets in the main window."""
        self.image_label = QLabel()
        self.image_label.setObjectName("ImageLabel")
        # Create various widgets for image processing in the side panel
        face_detected_label = QLabel("Face Detected Coordinates\n(TopLeftX, TopLeftY, BottomRightX, BottomRightY")
        #Now display the values in the rows under it
        
        
        self.draw_rectangle = QPushButton("Draw Rectangle")
        self.draw_rectangle.setEnabled(False)
        self.draw_rectangle.clicked.connect(self.draw_rectanglee)
        
        self.find_face = QPushButton("Find Face")
        self.find_face.setEnabled(True)

        self.next_btn = QPushButton("Next Image")
        self.next_btn.setEnabled(True)
        self.next_btn.clicked.connect(self.next_image)

        self.prev_btn = QPushButton("Previous Image")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.prev_image)

        #self.find_face.clicked.connect(self.faceRecognize)
        reset_button = QPushButton("Clear rectangle")
        reset_button.clicked.connect(self.resetImageAndSettings)
        # Create horizontal and vertical layouts for the side panel and main window
        side_panel_v_box = QVBoxLayout()
        side_panel_v_box.setAlignment(Qt.AlignTop)
        side_panel_v_box.addWidget(face_detected_label)
        #side_panel_v_box.addWidget(self.brightness_spinbox)
        side_panel_v_box.addSpacing(15)
        side_panel_v_box.addWidget(self.draw_rectangle)
        side_panel_v_box.addStretch(1)
        side_panel_v_box.addWidget(reset_button)
        side_panel_v_box.addWidget(self.next_btn)
        side_panel_v_box.addWidget(self.prev_btn)

        side_panel_frame = QFrame()
        side_panel_frame.setMinimumWidth(200)
        side_panel_frame.setFrameStyle(QFrame.WinPanel)
        side_panel_frame.setLayout(side_panel_v_box)
        main_h_box = QHBoxLayout()
        main_h_box.addWidget(self.image_label, 1)
        main_h_box.addWidget(side_panel_frame)
        # Create container widget and set main window's widget
        container = QWidget()
        container.setLayout(main_h_box)
        self.setCentralWidget(container)
    
    ##Change this to "Draw Rectangle thing"
    def draw_rectanglee(self):
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(QRect(self.origin, event.pos()).normalized())
    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            print(event.pos())
            print(self.origin)
            self.rubberband.hide()
    def next_image(self):
        
        self.prev_btn.setEnabled(True)
        
        
        if self.current_img == len(self.image_paths) - 1:
            self.current_folder = (self.current_folder + self.step_size) % len(self.id_folders)

        subject = self.id_folders[self.current_folder].split("/")[-1].split("\\")[-1]
        
        self.current_img = (self.current_img + self.step_size) % len(self.image_paths)

        with open(self.output_file, "a") as label_file:
            output_string = subject + ": " + self.image_paths[self.current_img-1].split("/")[-1] + "\n"
            label_file.write(output_string)
        
        self.current_image = self.image_paths[self.current_img]
        
        self.openImage()
        
        if (self.current_img == 0):
            self.prev_btn.setEnabled(False)

    def prev_image(self):
        
        self.current_img = (self.current_img - self.step_size) % len(self.image_paths)
        self.current_image = self.image_paths[self.current_img]

        if(self.current_img == 0):
            self.prev_btn.setEnabled(False)
        
        with open(self.output_file, "r") as label_file:
            lines = label_file.readlines()
            print(lines)
        with open(self.output_file, "w") as label_file:
            label_file.writelines(lines[:-1])
        
        
        self.openImage()
        

        
    def resetImageAndSettings(self):
        """Reset the displayed image and widgets used for image processing."""
        answer = QMessageBox.information(self, "Reset Image",
                "Are you sure you want to clear rectangles?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.No:
            pass
        elif answer == QMessageBox.Yes and self.image_label.pixmap() != None:
            #self.resetWidgetValues()
            self.cv_image = self.copy_cv_image
            self.convertCVToQImage(self.cv_image)
            cv2.imshow("ahh", self.cv_image)
    
    def openImage(self):
        image_file = self.current_image
        if image_file:

            self.draw_rectangle.setEnabled(True)
            self.cv_image = cv2.imread(image_file)
            self.copy_cv_image = self.cv_image.copy()
            

            gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
            frame = self.perform_face_recog(gray, self.cv_image)

            self.convertCVToQImage(frame)
            self.image_label.repaint()
        else:
            QMessageBox.information(self, "Error",
                "No image was loaded.", QMessageBox.Ok)

    def convertCVToQImage(self, image):
        """Load a cv image and convert the image to a Qt QImage. Display the image in image_label."""
        cv_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Get the shape of the image, height * width * channels. BGR/RGB/HSV images have 3 channels
        height, width, channels = cv_image.shape # Format: (rows, columns, channels)
        # Number of bytes required by the image pixels in a row; dependency on the number of channels
        bytes_per_line = width * channels
        # Create instance of QImage using data from cv_image
        converted_qt_image = QImage(cv_image, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(converted_qt_image).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio))
    def perform_face_recog(self, gray, frame):

        faces = face_cascade.detectMultiScale(gray, 1.4, 6)
        print(faces)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
            print(x,y, x+h, y+h)
        #cv2.imshow("imgz",frame)

        
        return frame


        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = ImageProcessingGUI()
    sys.exit(app.exec_())