#lock.acquire()#上锁方法1  如果上锁成功 返回True 如果已经上锁，就被阻塞
#lock.release()#解锁

import cv2 as cv
import time
import os
import numpy as np
import sklearn.preprocessing as sp

class FaceRecognition():
    def __init__(self):
        # 哈尔级联人脸定位器
        self.fd = cv.CascadeClassifier('ml_data/haar/face.xml')
        self.ed = cv.CascadeClassifier('ml_data/haar/eye.xml')
        self.nd = cv.CascadeClassifier('ml_data/haar/nose.xml')
        self.savePath = 'image/img/'
        self.train_faces = self.search_faces('image/img/')

    def delByName(self,name):
        directory = os.path.normpath('image/img/' + name)
        for curdir, subdirs, files in os.walk(directory):
            #删掉里面的照片
            for i in files:
                os.remove(curdir+'/'+i)



    def picCap(self,name,sec):
        logo = cv.imread('logo/logo.jpg')
        vc = cv.VideoCapture(0)
        t_end = time.time() + sec
        capturedNum = 0
        #删掉之前的照片
        self.delByName(name)

        cv.namedWindow(name, cv.WINDOW_AUTOSIZE)
        cv.setWindowProperty(name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        cv.moveWindow(name, 0, 0)

        print("请将脸放入摄像头范围，稍微动一动，对不同角度进行头像采集")
        while time.time() < t_end:
            frame = vc.read()[1]
            # 1.3 scaleFactor 表示在前后两次相继的扫描中，搜索窗口的比例系数。默认为1.1即每次搜索窗口依次扩大10%;
            # 5 minNeighbors 表示构成检测目标的相邻矩形的最小个数(默认为3个)。 如果min_neighbors 为 0, 则函数不做任何操作就返回所有的被检候选矩形框，
            faces = self.fd.detectMultiScale(frame, 1.3, 5)
            if len(faces)>0:
                capturedNum += 1
                cv.imwrite(self.savePath + '/' + name + '/' + str(capturedNum) + '.jpg',
                                frame)
                for l, t, w, h in faces:
                    a, b = int(w / 2), int(h / 2)
                    cv.ellipse(frame, (l + a, t + b),
                               (a, b), 0, 0, 360,
                               (255, 0, 255), 2)
                    face = frame[t:t + h, l:l + w]
                    eyes = self.ed.detectMultiScale(face, 1.3, 5)
                    for l, t, w, h in eyes:
                        a, b = int(w / 2), int(h / 2)
                        cv.ellipse(face, (l + a, t + b),
                                   (a, b), 0, 0, 360,
                                   (0, 255, 0), 2)
                    noses = self.nd.detectMultiScale(face, 1.3, 5)
                    for l, t, w, h in noses:
                        a, b = int(w / 2), int(h / 2)
                        cv.ellipse(face, (l + a, t + b),
                                   (a, b), 0, 0, 360,
                                   (0, 255, 255), 2)
                    cv.imshow(name, frame)
                    time.sleep(0.2)
            else:
                cv.imshow(name, frame)
            #按了ESC  33ms检测一次
            cv.waitKey(33)
        #判断采集是否成功 成功截图数是否够。
        directory = os.path.normpath('image/img/' + name)
        for curdir, subdirs, files in os.walk(directory):
            if len(files) > 5:
                print("采集成功")
                cv.imshow(type, logo)
                cv.waitKey(33)
                cv.destroyAllWindows()
                vc.release()
                return True
            else:
                print("采集失败")
                cv.imshow(type, logo)
                cv.waitKey(33)
                cv.destroyAllWindows()
                vc.release()
                return False


    def search_faces(self,directory):
        directory = os.path.normpath(directory)
        faces = {}
        for curdir, subdirs, files in os.walk(directory):
            for jpeg in (file for file in files
                         if file.endswith('.jpg')):
                path = os.path.join(curdir, jpeg)
                label = path.split(os.path.sep)[-2]
                if label not in faces:
                    faces[label] = []
                faces[label].append(path)
        return faces

    def trainModel(self):
        #{'hai':[url1,url2]

        self.codec = sp.LabelEncoder()
        self.codec.fit(list(self.train_faces.keys()))
        train_x, train_y = [], []
        for label, filenames in self.train_faces.items():
            for filename in filenames:
                image = cv.imread(filename)
                gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
                faces = self.fd.detectMultiScale(gray, 1.1, 2,
                                            minSize=(100, 100))
                for l, t, w, h in faces:
                    train_x.append(
                        gray[t:t + h, l:l + w])
                    train_y.append(
                        self.codec.transform([label])[0])
        train_y = np.array(train_y)
        # 局部二值模式直方图人脸识别分类器
        self.model = cv.face.LBPHFaceRecognizer_create()
        self.model.train(train_x, train_y)


    def predictFace(self,sec):
        vc = cv.VideoCapture(0)

        for i in range(10):
            frame = vc.read()[1]
            cv.waitKey(33)
        #只进行sec秒检测
        t_end = time.time() + sec
        while time.time() < t_end:
            frame = vc.read()[1]
            face = self.fd.detectMultiScale(frame,1.3,5)
            testFace = None
            if face != ():
                #print(frame)
                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                faces = self.fd.detectMultiScale(gray, 1.1, 2,
                                                 minSize=(100, 100))
                for l, t, w, h in faces:
                    testFace = gray[t:t + h, l:l + w]
                pred_code = self.model.predict(testFace)[0]
                pred_test_y = self.codec.inverse_transform([pred_code])
                #print(pred_test_y[0])
                break
            # 按了ESC  33ms检测一次
            cv.waitKey(500)
        else:
            cv.destroyAllWindows()
            vc.release()
            return 'vague'
        cv.destroyAllWindows()
        vc.release()
        return pred_test_y[0]

    def show(self,path,type):
        print('选中图片按ESC 关闭窗口')
        path = 'Message/body/stage1/1.jpg'
        src = cv.imread(path)
        cv.namedWindow(type, cv.WINDOW_AUTOSIZE)
        cv.setWindowProperty(type, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        cv.moveWindow(type, 0, 0)
        while True:
            #print(cv.getWindowProperty(type, cv.WND_PROP_AUTOSIZE))
            cv.imshow(type, src)
            k = cv.waitKey(33)

            if k == 27:
                break

        logo = cv.imread('logo/logo.jpg')
        cv.imshow(type, logo)
        cv.waitKey(33)
        cv.destroyAllWindows()

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.show('1','1')
    time.sleep(10)


