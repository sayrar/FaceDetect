from face_recog import DATA_FOLDER
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QGraphicsView, QHBoxLayout, QLabel, QMainWindow, 
        QGraphicsScene, QApplication, QPushButton, QRubberBand, QVBoxLayout, QGraphicsPixmapItem,
        QWidget, QMessageBox,)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QRect, QSize
import os, sys, cv2
import numpy as np

import platform
import glob

DATA_FOLDER = "downloads"

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') # We load the cascade for the face.

class FaceDetectionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initializeUI()
        

        


    def initializeUI(self):
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
        self.openImage()

        self.show()

    def setupWindow(self):
        self.scene = QGraphicsScene()
        self.graphicsView = GraphicsView()
        #self.scene.installEventFilter(self)
        self.graphicsView.setScene(self.scene)

        self.h_box = QVBoxLayout()
        self.v_box = QHBoxLayout()
        self.v_box.setAlignment(Qt.AlignLeft)
        self.clearRect = QPushButton("Clear Rectangle")
        self.clearRect.clicked.connect(self.clearRectangle)
        self.push = QPushButton("Previous Image")
        self.push.clicked.connect(self.prevImage)
        self.ok = QPushButton("Next Image")
        #Sself.ok.setEnabled(False)
        self.ok.clicked.connect(self.nextImage)

        self.v_box.addWidget(self.clearRect)
        self.v_box.addWidget(QPushButton("Draw Rectangle"))
        self.v_box.addStretch(1)
        self.v_box.addWidget(self.push)
        self.v_box.addWidget(self.ok)

        self.h_box.addWidget(self.graphicsView)
        self.image_size = QLabel()
        self.rect_coordinates = QLabel()
        self.h_box.addWidget(self.rect_coordinates)

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
        #self.graphicsView.setScene(self.scene)
    def drawRectangle():
        pass
    def nextImage(self):

        if self.graphicsView.rubberBand.isVisible():
            self.graphicsView.rubberBand.hide()
        #self.ok.setEnabled(True)

        #Check if the next image is the last one 
        #If it is, go to the next folder
        #if the next folder is the last folder, you're done (what next? D:)
        if self.cur_img_idx == len(self.image_paths) - 1:
            self.cur_dir_idx =  (self.cur_dir_idx+self.step) % len(self.image_paths)
            self.cur_img_idx = 0
        else:
            self.cur_img_idx = (self.cur_img_idx +self.step) % len(self.image_paths)

        self.cur_img = os.path.join(self.cur_dir, self.image_paths[self.cur_img_idx])

        self.openImage()
    
    def prevImage(self):

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
            #check if rectangle was drawn on 
            #self.resetWidgetValues()
            self.cv_image = self.copy_cv_image
            q_img = self.convertCV2QImage(self.cv_image)
            self.pic = QPixmap(q_img)
            self.showImage()
            cv2.imshow("ahh", self.cv_image)

            


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
            print(int(x),int(y), int(x+w ), int(y+h))
            self.rect_coordinates.setText("X1: " + str(int(x)) + " Y1: " + str(int(y)) + "\n"+
                                            "X2: " + str(int(x+w)) + " Y2 " + str(int(y+h)))

        #self.coords = (int(x), int(y), int(x+w), int(y+h))
        #print(self.coords)
        return frame
    """ def eventFilter(self, obj, event):
        if obj is self.scene and event.type() == QtCore.QEvent.GraphicsSceneMousePress:
            spf = event.scenePos()
            lpf = self.pixmap_item.mapFromScene(spf)
            brf = self.pixmap_item.boundingRect()
            if brf.contains(lpf):
                lp = lpf.toPoint()
                print("hehe " + str(lp))
        return super().eventFilter(obj, event) """

class GraphicsView(QGraphicsView):

    rectChanged = pyqtSignal(QRect)
    rectCoord = pyqtSignal(QPoint, QPoint)
    
    def __init__(self):
        QGraphicsView.__init__(self)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)
        self.setMouseTracking(True)
        self.origin = QPoint()
        self.changeRubberBand = False

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rectChanged.emit(self.rubberBand.geometry())
        self.rubberBand.show()
        self.changeRubberBand = True
        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.changeRubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
        QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.final_coord = event.pos()
        print(self.origin)
        print(event.pos())
        self.hehe = event.pos()
        self.changeRubberBand = False
        self.rectCoord.emit(self.hehe, self.origin)

        QGraphicsView.mouseReleaseEvent(self, event)
    def clearRect(self):
        self.rubberBand.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyleSheet(style_sheet)
    window = FaceDetectionGUI()
    sys.exit(app.exec_())

        