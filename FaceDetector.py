#from face_recog import DATA_FOLDER
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QGraphicsSceneMouseEvent, QGraphicsView, QHBoxLayout, QLabel, QMainWindow, 
        QGraphicsScene, QApplication, QPushButton, QRubberBand, QVBoxLayout, QGraphicsPixmapItem,
        QWidget, QMessageBox,)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QRect, QSize, QPointF
import os, sys, cv2
import numpy as np

import platform
import glob
import time
import csv
import re
DATA_FOLDER = "downloads"

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') # We load the cascade for the face.

class FaceDetectionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()
        

    def initializeUI(self):
        self.output_file = "session-{}.csv".format(time.time())

        self.cur_dir_idx = 0
        self.cur_img_idx = 0
        self.step = 1

        self._base_dir = os.getcwd()
        self._celeb_dir = os.path.join(self._base_dir, DATA_FOLDER, '')

        self.id_folders = sorted(os.listdir(self._celeb_dir))
        #print(self.id_folders)

        self.cur_dir = os.path.join(self._celeb_dir, '', self.id_folders[self.cur_dir_idx], '')
        
        
        self.image_paths = sorted(os.listdir(self.cur_dir))

        self.cur_img = self.image_paths[self.cur_img_idx]
        self.cur_img = os.path.join(self.cur_dir, self.image_paths[self.cur_img_idx])
        

        self.setMinimumSize(900, 600)
        self.setWindowTitle(self.id_folders[self.cur_dir_idx] + " " + str(self.cur_img_idx))
        self.setupWindow()
        self.checkSession()
        self.openImage()

        self.show()

    def setupWindow(self):
        self.scene = QGraphicsScene()
        self.graphicsView = GraphicsView()
        self.graphicsView.setScene(self.scene)

        self.h_box = QVBoxLayout()
        self.v_box = QHBoxLayout()
        self.v_box.setAlignment(Qt.AlignLeft)
        self.clearRect = QPushButton("Clear Rectangle")
        self.clearRect.clicked.connect(self.clearRectangle)
        self.push = QPushButton("Previous Image")
        self.push.setDisabled(True)
        self.push.clicked.connect(self.prevImage)
        

        self.ok = QPushButton("Next Image")
        #Sself.ok.setEnabled(False)
        self.ok.clicked.connect(self.nextImage)

        self.v_box.addWidget(self.clearRect)
        self.rectBtn = QPushButton("Draw Rectangle")
        self.rectBtn.setCheckable(True)
        #self.rectBtn.toggle()
        self.rectBtn.clicked.connect(self.drawRectangle)
        
        self.v_box.addWidget(self.rectBtn)
        self.v_box.addStretch(1)
        self.v_box.addWidget(self.push)
        self.v_box.addWidget(self.ok)

        self.h_box.addWidget(self.graphicsView)
        self.image_size = QLabel()
        self.rect_coordinates = QLabel()
        self.h_box.addWidget(self.rect_coordinates)

        self.mouse_coor = QLabel()
        self.h_box.addWidget(self.mouse_coor)

        self.graphicsView.rectCoord.connect(self.updateLayout)

        self.h_box.addWidget(self.image_size)
        self.h_box.addLayout(self.v_box)
        

        container = QWidget()
        container.setLayout(self.h_box)
        self.setCentralWidget(container)
    
    def openImage(self):

        if self.cur_img:
            self.cv_image = cv2.imread(self.cur_img)
            self.copy_cv_image = self.cv_image.copy()

            image = self.detectFaces(self.cv_image)

            q_img = self.convertCV2QImage(image)

            self.pic = QPixmap(q_img)

            self.showImage()
            self.image_size.setText(str(self.pic.size().width()) + "x" + str(self.pic.size().height()))

    def showImage(self):
        
        self.scene.clear()
        self.pixmap_item = self.scene.addPixmap(self.pic)
        self.graphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def drawRectangle(self):
        
        if self.rectBtn.isChecked():
            self.graphicsView.rectBtnPressed()
        else:
            self.graphicsView.rectBtnOff()
            self.graphicsView.clearRect()
        
    def nextImage(self):
        self.push.setDisabled(False)
        self.rectBtn.setChecked(False)
        self.graphicsView.rectBtnOff()
        self.graphicsView.clearRect()


        self.save_csv(1)

        #Check if the next image is the last one 
        #If it is, go to the next folder
        #if the next folder is the last folder, you're done (what next? D:)

        if self.cur_img_idx == len(self.image_paths) - 1:

            self.cur_dir_idx =  (self.cur_dir_idx+self.step) % len(self.image_paths)
            self.cur_img_idx = 0
            
        else:
            self.cur_img_idx = (self.cur_img_idx +self.step) % len(self.image_paths)
        self.cur_dir = os.path.join(self._celeb_dir, '', self.id_folders[self.cur_dir_idx], '')
        
        
        self.image_paths = sorted(os.listdir(self.cur_dir))
        self.cur_img = os.path.join(self.cur_dir, self.image_paths[self.cur_img_idx])
        self.setWindowTitle(self.id_folders[self.cur_dir_idx] + ": " + str(self.cur_img_idx) + "/" + str(len(self.image_paths)))
        self.openImage()
    
    def prevImage(self):
        if self.cur_dir_idx == 0 and self.cur_img_idx == 1:
            self.push.setDisabled(True)
        if self.cur_img_idx == 0:
            self.cur_dir_idx = (self.cur_dir_idx - self.step) % len(self.image_paths)
            self.cur_dir = os.path.join(self._celeb_dir, '', self.id_folders[self.cur_dir_idx])
            self.image_paths = sorted(os.listdir(self.cur_dir))

        self.rectBtn.setChecked(False)

        self.cur_img_idx = (self.cur_img_idx - self.step) %len(self.image_paths)


        self.cur_img = os.path.join(self.cur_dir, self.image_paths[self.cur_img_idx])
        print(self.cur_img_idx)

        self.openImage()

    def clearRectangle(self):
        """Reset the displayed image and widgets used for image processing."""
        answer = QMessageBox.information(self, "Reset Image",
                "Are you sure you want to clear rectangles?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.No:
            pass
        elif answer == QMessageBox.Yes:

            self.cv_image = self.copy_cv_image
            q_img = self.convertCV2QImage(self.cv_image)
            self.pic = QPixmap(q_img)
            self.showImage()

            self.graphicsView.clearRect()
            self.x1 = 0
            self.x2 = 0
            self.y1 = 0
            self.y2 = 0


    def convertCV2QImage(self, cv_img):
        cv_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        height, width, channels = cv_image.shape
        bytes_per_line = width * channels

        converted = QImage(cv_image, width, height, bytes_per_line, QImage.Format_RGB888)
    
        return converted

    def detectFaces(self, frame):
        #convert to gray
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        

        faces = face_cascade.detectMultiScale(gray, 1.4, 6)


        for (x, y , w, h) in faces:
            rw = w
            rh = h

            w = (w * 1.25) #/ 100.0
            h = h * 1.25 #/ 100

            x = x + (rw - w)/2
            y = y + (rh-h)/2

            cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)), (255,0,0), 2)

            self.x1 = int(x)
            self.y1 = int(y)

            self.x2 = int(x +w)
            self.y2 = int(y+h)
            self.rectType = "auto"

            self.rect_coordinates.setText("X1: " + str(self.x1) + "\tY1: " + str(self.y1) + "\t"+
                                            "X2: " + str(self.x2) + "\t " +"Y2: " + str(self.y2))
        return frame

    def save_csv(self, type):
        if type ==1:
            img_data = [self.id_folders[self.cur_dir_idx], self.image_paths[self.cur_img_idx], self.x1, self.y1, self.x2, self.y2,self.rectType]
            print(self.id_folders[self.cur_dir_idx])
            with open(self.output_file, "a") as label_file:
                
                writer = csv.writer(label_file)

                writer.writerow(img_data)
        if type == 2:
            f = open(self.output_file, "r+w")
            lines=f.readlines()
            lines=lines[:-1]

            writee = csv.writer(f, delimiter=',')
            for line in lines:
                writee.writerow(line)

    def updateLayout(self, point1, point2):
        self.x1 = point1.x()
        self.y1 = point1.y()

        self.x2 = point2.x()
        self.y2 = point2.y()
        self.rectType = "manual"

        print("here")

        self.rect_coordinates.setText("X1: " + str(self.x1) + "\tY1: " + str(self.y1) + "\t"+
                                            "X2: " + str(self.x2) + "\t " +"Y2: " + str(self.y2))
        
    def checkSession(self):
        files = glob.glob("./*")
        for path in reversed(sorted(files)):
            prev_session = re.search("")
            if path:
                return prev_session


class GraphicsView(QGraphicsView):

    rectChanged = pyqtSignal(QRect)
    rectCoord = pyqtSignal(QPoint, QPoint)
    currCood = pyqtSignal(QPoint)
    

    def __init__(self):
        QGraphicsView.__init__(self)
        self.canDraw = False
        self.rectDrawn = False
        self.rubberBand = None
        
    def rectBtnPressed(self):
        self.canDraw = True
        
        self.setMouseTracking(True)
        self.origin = QPoint()
        self.changeRubberBand = False

    def rectBtnOff(self):
        print("Unchecked")
        self.setMouseTracking(False)
        self.canDraw = False

    def mousePressEvent(self, event):
        if self.canDraw == False:
            return
        self.origin = event.pos()
        if self.rubberBand is None:
            self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rectChanged.emit(self.rubberBand.geometry())
        self.rubberBand.show()
        self.changeRubberBand = True
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.canDraw == False:
            
            return
        if self.changeRubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
            
        QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.canDraw == False:
            return
        self.final_coord = event.pos()
        self.hehe = event.pos()
        self.changeRubberBand = False
        print(self.mapToScene(self.hehe), self.mapToScene(self.origin))
        self.rectCoord.emit(self.mapToScene(self.origin).toPoint(), self.mapToScene(self.hehe).toPoint())
        self.rectDrawn = True

        

        QGraphicsView.mouseReleaseEvent(self, event)
    def clearRect(self):
        if self.rectDrawn:
            self.rubberBand.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyleSheet(style_sheet)
    window = FaceDetectionGUI()
    sys.exit(app.exec_())


        