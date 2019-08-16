from PyQt5.QtWidgets import QApplication, QPushButton, QMessageBox, QLabel, QHBoxLayout, QTextEdit, QMainWindow,QDialog
from PyQt5.QtGui import QPixmap,QFont
from PyQt5.Qt import QLineEdit
from PyQt5.QtCore import pyqtSlot,QTimer,QUrl
import sys
from PyQt5 import QtGui,QtMultimedia
import jieba
import re
from src import certainlyModel, faceModel as fm, actionModel
import pyaudio
import wave
import signal
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
import cv2 as cv
import face_recognition
import os
import time
import threading
#for pyinstaller
#import numpy.random.entropy
#import distutils
#import distutils.dist

class GameImg(QDialog):
    def __init__(self,path,type):
        QDialog.__init__(self)
        hbox = QHBoxLayout(self)
        lbl = QLabel(self)
        pixmap = QPixmap(path)  # 按指定路径找到图片，注意路径必须用双引号包围，不能用单引号
        lbl.setPixmap(pixmap)  # 在label上显示图片
        lbl.setScaledContents(True)  # 让图片自适应label大小
        hbox.addWidget(lbl)
        self.setLayout(hbox)
        self.move(300, 200)
        self.setWindowTitle(type)
        self.show()



class GameUi(QMainWindow):
    def __init__(self, game):
        # ui
        QMainWindow.__init__(self)
        # super().__init__()
        self.title = '《假象》'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 800
        self.font = QFont("宋体")
        self.pointsize = self.font.pointSize()
        self.font.setPixelSize(self.pointsize * 90 / 72)
        app.setFont(self.font)

        self.game = game
        self.child1 = None
        self.child2 = None
        self.child3 = None
        self.child4 = None
        self.child5 = None
        self.child6 = None
        self.child7 = None
        self.child8 = None
        self.child9 = None
        self.imgList=[self.child1,self.child2,self.child3,self.child4,self.child5,self.child6,self.child7,self.child8,self.child9]
        self.map1 = None
        self.map2 = None
        self.specialMessage = None

        self.timer_camera1 = QTimer()  # 定义定时器，用于截取图片
        self.timer_camera2 = QTimer()  # 定义定时器，只显示图像


        #初始化槽函数
        self.capturename = None
        self.timer_camera1.timeout.connect(lambda:self.show_camera(self.capturename, 'picCap'))
        self.timer_camera2.timeout.connect(lambda:self.show_camera(None,'Play'))

        self.capturedNum = 3

        self.cap = cv.VideoCapture(0)  # 视频流

        self.cameraJustPlay()

        # self.displayTimer = QTimer()
        # self.displayStr = ""
        # self.displayTimer.timeout.connect(lambda :self.myPrint_delay(self.displayStr))

        self.currentVoicePath = None
        self.playVoice = QTimer()
        self.playVoice.timeout.connect(lambda :self.play(self.currentVoicePath))


    def delByName(self,name):
        directory = os.path.normpath('resources/image/img/' + name)
        for curdir, subdirs, files in os.walk(directory):
            #删掉里面的照片
            for i in files:
                os.remove(curdir+'/'+i)

    def myPrint(self, sent):
        self.textbox2.setText(sent)

    # def myPrint_delay(self,sent):
    #     value = self.textbox2.toPlainText()
    #     if len(value) < len(sent):
    #         s = sent[0:len(value)+1]
    #         self.textbox2.setText(s)
    #     else:
    #         self.displayTimer.stop()

    def textbox2Clear(self):
        self.textbox2.setText("")

    def prestart(self,extra):
        unrecordList = self.game.getUnrecordList()

        # self.displayStr = extra + "请各位玩家依次录入人脸信息\n\n请输入角色名称，之后请看摄像头\n\n录入过程中，请确保身后没有其他玩家\n\n当前没有录入的玩家为:" + ' '.join(unrecordList)
        # self.textbox2Clear()
        # self.displayTimer.start(100)
        self.myPrint(extra + "请各位玩家依次录入人脸信息（捕捉图像时可能会有小的延迟卡顿，请等待）\n\n请输入角色名称，之后请看摄像头\n\n录入过程中，请确保身后没有其他玩家\n\n当前没有录入的玩家为:" + ' '.join(unrecordList))

    def initUI(self):
        str1 = "我是一个剧本AI主持人，在这个剧本杀中，我会尝试去理解你们说的话（如果没有理解请尝试换种说法T-T, 毕竟..我这种学渣刚及格的水平..）。" \
              "\n在界面下方文本框内，输入想做的事情，并按下 -->回车键<-- 与我进行交互。（交互过程中，摄像头亮起为人脸识别过程，请看摄像头并且耐心等待。）\n" \
              "我会打开摄像头来判断正在跟我交互的玩家。所以，无论是在人脸录入和与我交互的过程中，请确保你的身后没有别的玩家。\n" \
              "\n首先请让我介绍一下这个剧本，这个剧本杀的名字叫做《假象》。繁华的都市总让人浮想联翩，公州大学，一个人才济济的地方。不过有光的地方就有阴影，最阳光的校园往往藏着最肮脏的角落。当尘埃落定，一切都为虚妄的假象\n" \
               "各位好，我是张警官，就在刚刚宁国教授被发现死于自己的办公室内，警方不排除他杀的可能，经过初步调查，警方把今天在案发楼层出现过的所有人聚集在此，并通知大家，整个学校已经封锁。等待进一步调查，调查期间你们6人只可在校园内活动。\n" \
               "\n进入第1阶段： 在本阶段中，请玩家仔细阅读第一幕，并且避免被其他玩家看到" \
               "阅读完之后，请玩家自行决定搜查顺序，来我这里进行搜查。所有玩家可以自由讨论\n\n" \
               "共有3个搜查阶段，1个投票阶段，和1个复盘的阶段。\n每个搜查阶段中，每个玩家可以搜查3条线索，个别线索可以深入调查，而深入调查只能在第2、3阶段进行，并且会消耗一次搜查机会。\n" \
               "当所有玩家完成本轮搜查，则可以\"进入下一阶段\"\n\n" \
               " 提示： 1）直接输入人名或一句话均可；\n 2）本轮搜查中，根据玩家的搜查进度，可触发公共的特殊线索，请注意点击 -->特殊线索<-- 查看；\n 3）所有搜查完成后，可以'进入下个阶段'"
        # self.textbox2Clear()
        # self.displayTimer.start(100)
        self.myPrint(str1)

        self.currentVoicePath = 'resources/Sound/stage1.wav'
        self.playVoice.start(1000)

        #self.map1 = GameImg('resources/map/1.jpg', '公共线索：室内平面图')


    def window(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(40, 600)
        self.textbox.resize(750, 50)

        # create textbox2 (background)
        self.textbox2 = QTextEdit(self)
        self.textbox2.move(40, 40)
        self.textbox2.resize(350, 480)

        # Create a button in the window
        self.button = QPushButton('公共线索', self)
        self.button.move(850, 610)
        self.button.setStyleSheet("QPushButton{color:#e8f0de}"
                                  "QPushButton{outline:none}"
                                  "QPushButton{text-align:center}"
                                  "QPushButton{text-decoration:none}"
                                  "QPushButton{padding:.35em 1em .55em}"
                                  "QPushButton{background:#64991e}"
                                  "QPushButton{border:solid 1px #538312}"
                                  "QPushButton:hover{text-decoration:none}"
                                  "QPushButton:hover{background:#538018;}"
                                  "QPushButton{border-radius:15px;}"
                                  )
        self.button2 = QPushButton('特殊线索', self)
        self.button2.move(1000, 610)
        self.button2.setStyleSheet("QPushButton{color:#e8f0de}"
                                  "QPushButton{outline:none}"
                                  "QPushButton{text-align:center}"
                                  "QPushButton{text-decoration:none}"
                                  "QPushButton{padding:.35em 1em .55em}"
                                  "QPushButton{background:#64991e}"
                                  "QPushButton{border:solid 1px #538312}"
                                  "QPushButton:hover{text-decoration:none}"
                                  "QPushButton:hover{background:#538018;}"
                                  "QPushButton{border-radius:15px;}"
                                  )


        self.label_show_camera = QLabel(self)  # 定义显示视频的Label
        self.label_show_camera.move(480, 40)
        self.label_show_camera.setFixedSize(641, 481)  # 给显示视频的Label设置大小为641x481

        # connect button to function on_click
        self.button.clicked.connect(self.showPublicMessage)
        self.button2.clicked.connect(self.showSpecialMessage)
        self.show()

    def closeProgram(self):
        self.close()

    def windowResize(self):
        self.textbox2.move(130, 40)
        self.textbox2.resize(900, 480)
        self.textbox.move(130, 600)
        self.textbox.resize(750, 50)
        self.button.move(900, 610)
        self.button2.move(1020, 610)

    def showSpecialMessage(self):
        if self.game.computerAndUdisk:
            self.specialMessage = GameImg('resources/Message/special/1.jpg',"特殊线索")
        else:
            QMessageBox.question(self, 'Message', '尚未解锁特殊线索',
                                 QMessageBox.Ok, QMessageBox.Ok)

    def showPublicMessage(self):
        if self.game.getCurrentStage() <= 1:
            self.map1 = GameImg('resources/map/1.jpg', '公共线索：室内平面图')
        else:
            self.map1 = GameImg('resources/map/1.jpg', '公共线索：室内平面图')
            self.map2 = GameImg('resources/map/2.jpg', '公共线索：实验楼剖面图')

    def show_camera(self,name,method):
        #print('name:',name,'method:',method)
        #30毫秒一针
        flag, self.image = self.cap.read()  # 从视频流中读取
        #print("self.image",self.image)
        if self.image is not None:
            show = cv.resize(self.image, (640, 480))  # 把读到的帧的大小重新设置为 640x480
            show = cv.cvtColor(show, cv.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0],
                                         QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
            if method == 'picCap' and name is not None:
                print('name:', name, 'method:', method)
                return self.picCap(name,self.image)
            elif method == 'predict':
                pass

    def open_camera_picCap(self,name):
        if self.timer_camera2.isActive():
            self.timer_camera2.stop()
        time.sleep(0.1)
        self.capturename = name
        #self.timer_camera1.timeout.connect(lambda: self.show_camera(name, 'picCap'))
        # 初始化 已录制张数
        self.capturedNum = 0
        self.timer_camera1.start(100)

    def cameraJustPlay(self):
        if self.timer_camera1.isActive():
            self.timer_camera1.stop()
        time.sleep(0.1)
        self.capturename = None
        self.timer_camera2.start(30)

    def close_camera(self):
        self.timer_camera1.stop()  # 关闭定时器
        self.timer_camera2.stop()  # 关闭定时器
        self.cap.release()  # 释放视频流
        self.label_show_camera.clear()  # 清空视频显示区域

    def picCap(self,name,image):
        print("picCap:", name)
        self.savePath = 'resources/image/img/'
        print("请将脸放入摄像头范围，稍微动一动")
        if self.capturedNum <=1:
            faces = face_recognition.face_locations(image)
            print(faces)
            if len(faces) == 1:
                self.capturedNum += 1
                cv.imwrite(self.savePath + '/' + name + '/' + str(self.capturedNum) + '.jpg',
                           image)
                time.sleep(0.5)
        elif self.capturedNum == 2:
            faces = face_recognition.face_locations(image)
            print(faces)
            if len(faces) == 1:

                self.capturedNum += 1
                cv.imwrite(self.savePath + '/' + name + '/' + str(self.capturedNum) + '.jpg',
                           image)
                #self.close_camera()
                words = 'false'
                directory = os.path.normpath('resources/image/img/' + name)
                for curdir2, subdirs2, files2 in os.walk(directory):
                    if len(files2) > 2:
                        self.game.recordFace[name] = True
                        words = 'done'
                    else:
                        self.game.recordFace[name] = False
                        words = 'false'
                if words == 'false':
                    QMessageBox.question(self, 'Message', '录入失败',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.prestart('')
                    self.cameraJustPlay()
                elif words == 'done':
                    unrecordList = self.game.getUnrecordList()
                    if len(unrecordList) > 0:
                        QMessageBox.question(self, 'Message', '录入成功',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.prestart('')
                        self.cameraJustPlay()
                    else:
                        # self.displayTimer.timeout.connect(lambda: self.myPrint("人脸模型计算中..."))
                        # self.displayTimer.start(100)
                        self.myPrint("人脸模型计算中...")
                        self.game.fr.trainModel()
                        self.game.nextStage()
                        self.close_camera()
                        self.windowResize()
                        QMessageBox.question(self, 'Message', '计算完毕，准备工作完毕',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("请问是否开始游戏，记得把电脑的声音打开！")
                        # self.displayStr = "请问是否开始游戏？"
                        # self.textbox2Clear()
                        # self.displayTimer.start(100)
        else:
            pass

    def keyPressEvent(self, event):
        if str(event.key()) == '16777220':  # 回车
            self.on_click()

    @pyqtSlot()
    def on_click(self):
        self.clearScreen()
        textboxValue = self.textbox.text()

        stage = self.game.getCurrentStage()

        if stage == -1:

            QMessageBox.question(self, 'Message', '录入过程中，请确保摄像头范围没有其他玩家',
                                         QMessageBox.Ok, QMessageBox.Ok)

            name = self.game.findName(textboxValue)
            if name == 'vague':
                self.myPrint("抱歉，无法识别您输入的角色名称,请重新输入")
                self.textbox.setText('')
                return

            # 判断采集是否成功 成功截图数是否够。

            directory = os.path.normpath('resources/image/img/' + name)
            for curdir, subdirs, files in os.walk(directory):
                if len(files) > 1:
                    #exist
                    reply = QMessageBox.question(self, 'Message', '已经录入过您的人脸信息，是否重新录入\n\n录入过程中，请确保摄像头范围内没有其他玩家',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        #删掉之前的照片
                        self.delByName(name)
                        self.open_camera_picCap(name)
                    else:
                        self.prestart('')
                else:
                    #删掉之前的照片
                    self.delByName(name)
                    self.open_camera_picCap(name)

        elif stage == 0:
            r = self.game.cm.predictCertainly(textboxValue)
            if r == 'true':
                self.initUI()
                self.game.nextStage()
            else:
                if r == 'vague':
                    if self.game.am.predictAction(textboxValue) == 'start':
                        self.initUI()
                        self.game.nextStage()
                if self.game.getStartTimes() == 0:
                    self.myPrint('请准备好了告诉我\n')
                    self.game.increaseStartTimes()
                elif self.game.getStartTimes() == 1:
                    self.myPrint('请不要调戏我，准备好了就告诉我哦！下次无论如何开始了哦\n')
                    self.game.increaseStartTimes()
                elif self.game.getStartTimes() >= 2:
                    #self.myPrint('不等了，不等了，我们还是开始吧！\n')
                    self.initUI()
                    self.game.nextStage()

        elif stage <= 3 and stage > 0:
            name = self.game.detectFace()
            xs = re.compile(r'\d{6}')
            r = xs.findall(textboxValue)
            if len(r) > 0 and self.game.passwordLeft > 0 and self.game.passwordName == name:
                if r[0] == self.game.password:
                    QMessageBox.question(self, 'Message', '柜子里有一双被福尔马林浸泡的双足，其中右脚脚踝处有一个桃花形的胎记。',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                    self.textbox.setText('')
                    return
                else:
                    if self.game.passwordLeft >0:
                        self.game.passwordLeft -= 1
                    QMessageBox.question(self, 'Message', '还剩下'+str(self.game.passwordLeft)+"次输入密码的机会",
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                    self.textbox.setText('')
                    return

            text, searchDict = self.game.predictAction(textboxValue)
            print(text, searchDict)
            if text == 'own':
                self.myPrint('你好'+self.game.getChineseName(name))
                ownlist = self.game.ownMessage(name)
                if len(ownlist)>0 and type(ownlist) is list:
                    for i in range(len(ownlist)):
                        fl = re.compile(r'Message/(.*?)/')
                        p = fl.findall(ownlist[i])
                        if len(p)>0:
                            self.imgList[i] = GameImg(ownlist[i], self.game.nameMapForLabel.get(p[0]))
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+'显示您的线索完成\n\n显示多条线索有重叠情况，请自行拖动一下\n\n请告诉我还想做些什么?\n\n'+self.game.getLeftMessage())
                else:
                    QMessageBox.question(self, 'Message', '您尚未拥有线索',
                                                 QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+'想做些什么请直接告诉我\n\n'+self.game.getLeftMessage())

            elif text == 'searchNoNum':
                #self.myPrint('请告诉我你想要搜查的线索数量\n')
                searchDict['num'] = [1]
                # 判断是否为深入调查
                if '深' in textboxValue:
                    r = self.game.goDeep(searchDict, name)
                    if r == 'noPreMessage':
                        QMessageBox.question(self, 'Message', '您尚未掌握前置线索哦!',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'deepSearchNoPerson':
                        QMessageBox.question(self, 'Message', '您掌握多个人的前置线索，请使用"深入调查+角色名"进行深入调查？\n例如：深入调查隔壁老王',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+'提示：可以通过"我的线索"查看您已有的线索\n\n' + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'alreadyHave':
                        QMessageBox.question(self, 'Message', '您已经掌握该前置线索',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"那么现在您想做些什么呢？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'noDeepForPerson':
                        QMessageBox.question(self, 'Message', '该玩家没有深入线索。请您"查看我的线索"，看看该条属于谁的线索(在牌的最上方)',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请问有什么可以帮您？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'notEnoughMessage':
                        QMessageBox.question(self, 'Message', '您已经用完三次搜查机会了，请下回合再搜查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'IncorrectStage':
                        QMessageBox.question(self, 'Message', '本轮无法进行深入调查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    else:
                        print(r)
                        p = re.findall(r'deep/(.*?).jpg',r)[0]
                        self.imgList[0] = GameImg(r, self.game.nameMapForLabel.get(p))
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return

                if name == searchDict.get('place'):
                    QMessageBox.question(self, 'Message', '无法搜查自己的线索，天啦撸，你是凶手吧？竟然想搜自己！',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n"+self.game.getLeftMessage())
                else:
                    self.myPrint('你好' + self.game.getChineseName(name))
                    words,searchList = self.game.doSearch(searchDict, name)
                    s=''
                    if len(searchList)>0:
                        s = '千万别忘记离开时关掉自己的线索，以免被别的玩家看到\n\n'
                        for i in range(len(searchList)):
                           self.imgList[i] = GameImg(searchList[i], self.game.nameMapForLabel.get(searchDict.get('place')))
                    if words is not None:
                        QMessageBox.question(self, 'Message', words,
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+s+self.game.getLeftMessage())


            elif text == 'search':
                # 判断是否为深入调查
                if '深' in textboxValue:
                    r = self.game.goDeep(searchDict, name)
                    if r == 'noPreMessage':
                        QMessageBox.question(self, 'Message', '您尚未掌握前置线索哦!',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'deepSearchNoPerson':
                        QMessageBox.question(self, 'Message', '您掌握多个人的前置线索，请使用"深入调查+角色名"进行深入调查？\n例如：深入调查隔壁老王',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+'提示：可以通过"我的线索"查看您已有的线索\n\n' + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'alreadyHave':
                        QMessageBox.question(self, 'Message', '您已经掌握该前置线索',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"那么现在您想做些什么呢？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'noDeepForPerson':
                        QMessageBox.question(self, 'Message', '该玩家没有深入线索。请您"查看我的线索"，看看该条属于谁的线索(在牌的最上方)',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请问有什么可以帮您？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'notEnoughMessage':
                        QMessageBox.question(self, 'Message', '您已经用完三次搜查机会了，请下回合再搜查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'IncorrectStage':
                        QMessageBox.question(self, 'Message', '本轮无法进行深入调查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    else:
                        print(r)
                        p = re.findall(r'deep/(.*?).jpg',r)[0]
                        self.imgList[0] = GameImg(r, self.game.nameMapForLabel.get(p))
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return

                if name == searchDict.get('place'):
                    QMessageBox.question(self, 'Message', '无法搜查自己的线索，天啦撸，你是凶手吧？竟然想搜自己！',
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n"+self.game.getLeftMessage())
                else:
                    self.myPrint('你好' + self.game.getChineseName(name))
                    words,searchList = self.game.doSearch(searchDict, name)
                    s=''
                    if len(searchList)>0:
                        s = '显示多条线索有重叠情况，请自行拖动一下\n\n另外千万别忘记离开时关掉自己的线索，以免被别的玩家看到\n\n'
                        for i in range(len(searchList)):
                            self.imgList[i] = GameImg(searchList[i], self.game.nameMapForLabel.get(searchDict.get('place')))
                    if words is not None:
                        QMessageBox.question(self, 'Message', words,
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+s+self.game.getLeftMessage())
            elif text == 'vague':
                self.myPrint('抱歉，我智商不足\n\n没能识别您说的话，请换种方式试试\n\n或者你想给我的智商充值也可以\n\n我的支付宝是：182xxxxxx\n\n'+self.game.getLeftMessage())

            elif text == 'searchNoPerson':
                # 判断是否为深入调查
                if '深' in textboxValue:
                    r = self.game.goDeep(searchDict, name)
                    if r == 'noPreMessage':
                        QMessageBox.question(self, 'Message', '您尚未掌握前置线索哦!',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'deepSearchNoPerson':
                        QMessageBox.question(self, 'Message', '您掌握多个人的前置线索，请使用"深入调查+角色名"进行深入调查？\n例如：深入调查隔壁老王',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+'提示：可以通过"我的线索"查看您已有的线索\n\n' + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'alreadyHave':
                        QMessageBox.question(self, 'Message', '您已经掌握该前置线索',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"那么现在您想做些什么呢？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'noDeepForPerson':
                        QMessageBox.question(self, 'Message', '该玩家没有深入线索。请您"查看我的线索"，看看该条属于谁的线索(在牌的最上方)',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请问有什么可以帮您？\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'notEnoughMessage':
                        QMessageBox.question(self, 'Message', '您已经用完三次搜查机会了，请下回合再搜查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    elif r == 'IncorrectStage':
                        QMessageBox.question(self, 'Message', '本轮无法进行深入调查',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return
                    else:
                        print(r)
                        p = re.findall(r'deep/(.*?).jpg',r)[0]
                        self.imgList[0] = GameImg(r, self.game.nameMapForLabel.get(p))
                        self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+"请告诉我你想做的事情\n\n" + self.game.getLeftMessage())
                        self.textbox.setText('')
                        return

                QMessageBox.question(self, 'Message', '如果您想要搜查，请至少告诉我想要搜查谁？',
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.myPrint("当前为第"+str(self.game.getCurrentStage())+"阶段\n"+self.game.getLeftMessage())

            elif text == 'next':

                if stage < 3:
                    reply = QMessageBox.question(self, 'Message', '确认进入下个阶段？若进入下个阶段，所有玩家将终止此轮搜查，可搜查的线索数也会更新哦',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                else:
                    reply = QMessageBox.question(self, 'Message', '下个阶段为投票阶段，请讨论并分别给出投票结果，投票阶段无法继续搜查，请问是否进入投票阶段？',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    self.game.nextStage()
                    if self.game.getCurrentStage() == 2:
                        self.game.resetEnable()
                        self.map2 = GameImg('resources/map/2.jpg','公共线索：实验楼剖面图')
                        self.myPrint('进入第2阶段：请各位仔细阅读第二幕\n本轮中，若有玩家搜到吴有为办公室锁住的柜子线索卡，有三次输入密码的机会。所有玩家开启下一轮搜查，请告诉我你想做的事情\n\n若误操作进入此轮搜查，在任何玩家还未搜查的前提下，可使用命令 "返回上一阶段" 返回\n')
                        self.currentVoicePath = 'resources/Sound/stage2.wav'
                        self.playVoice.start(1000)
                    elif self.game.getCurrentStage() == 3:
                        self.game.resetEnable()
                        self.myPrint('进入第3阶段：警方传来线索：警方在白芷莳的口鼻中发现了大量的乙醚\n\n所有玩家开启下一轮搜查，请告诉我你想做的事情\n\n若误操作进入此轮搜查，在任何玩家还未搜查的前提下，可使用命令 "返回上一阶段" 返回\n')
                        self.currentVoicePath = 'resources/Sound/stage3.wav'
                        self.playVoice.start(1000)
                    elif self.game.getCurrentStage() == 4:
                        self.game.resetEnable()
                        self.myPrint("进入第4阶段：进入投票阶段，请依次对杀死 -->宁国的凶手<--  ->白芷莳的凶手<-- 投票 \n\n首先投票杀死 -->宁国<-- 的凶手 \n\n若误操作进入此轮搜查，可使用命令 '返回上一阶段' 返回,投票后无法返回\n")
                else:
                    self.myPrint('没想好就再等等吧。想做什么可以直接跟我说\n\n'+self.game.getLeftMessage())
            elif text == 'previous':
                reply = QMessageBox.question(self, 'Message', '确认返回上个阶段？',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    if self.game.getEnable():
                        self.game.previousStage()
                        QMessageBox.question(self, 'Message', '所有玩家已经返回上一阶段',
                                             QMessageBox.Ok, QMessageBox.Ok)

                        self.myPrint("请告诉我想要做的事情，当前为第"+str(self.game.getCurrentStage())+"阶段 \n\n"+self.game.getLeftMessage())
                    else:
                        QMessageBox.question(self, 'Message',
                                             '本轮已有玩家搜查，无法返回，看来你们只能硬着头皮继续搜了',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint(self.game.getLeftMessage())
                else:
                    self.myPrint('既然不进行下一阶段，那么有啥事直接跟我说呗？\n\n'+self.game.getLeftMessage())


        elif stage == 4:
            text, searchDict = self.game.predictAction(textboxValue)
            if text == 'previous':
                reply = QMessageBox.question(self, 'Message', '确认返回上个阶段？',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    if self.game.getEnable():
                        self.game.previousStage()
                        QMessageBox.question(self, 'Message',
                                             '所有玩家已经返回上一阶段',
                                             QMessageBox.Ok, QMessageBox.Ok)
                        self.myPrint("请告诉我还想要做什么事情？\n\n当前为第"+str(self.game.getCurrentStage())+"阶段"+self.game.getLeftMessage())
                    else:
                        self.myPrint("本轮已有玩家投票，无法返回\n\n看来你们只能投票了")
                else:

                    self.myPrint('既然不返回，就来投票吧\n\n告诉我你想投谁？')
            else:
                doName = self.game.detectFace()
                if self.game.doVote.get(doName):
                    #投白芷莳  宁国投完
                    if self.game.doVote2.get(doName):
                        #白芷莳也投完了
                        self.myPrint("您已完成投票\n\n请未投票的玩家来进行投票")
                    else:
                        votedName = self.game.findName(textboxValue)
                        if votedName != 'vague' and doName != 'vague':
                            l = self.game.vote2(votedName, doName)
                            if len(l) > 0:
                                wordsstr = " ".join(l)
                                self.myPrint("未投票玩家: " + wordsstr + "\n\n请来找我投杀死 -->宁国<-- 的凶手")
                            else:
                                self.game.nextStage()
                                killerList = self.game.findKillerList()
                                str1 = '被投票最多杀死  -->宁国<-- 的凶手是：'
                                for i in killerList:
                                    str1 += self.game.nameMap.get(i) + ' '
                                killerList2 = self.game.findKillerList2()
                                str1 += '\n\n被投票最多杀死  -->白芷莳<-- 的凶手是：'
                                for i in killerList2:
                                    str1 += self.game.nameMap.get(i) + ' '
                                self.myPrint('\n投票结果:\n'+str1 + '\n\n准备好看复盘了么，好了的话告诉我哦！')
                        else:
                            self.myPrint("抱歉，不能识别您说的话,没找到您要投票的人\n\n请尽量保持文字正确哦。 >^<\n\n请来找我投杀死 -->宁国<-- 的凶手")
                else:
                    #投宁国
                    votedName = self.game.findName(textboxValue)
                    if votedName != 'vague' and doName != 'vague':
                        self.game.vote(votedName,doName)
                        self.myPrint("你好，"+self.game.nameMap.get(doName)+"\n\n请您继续投杀死  ->白芷莳<-- 的凶手")
                    else:
                        self.myPrint("抱歉，不能识别您说的话,没找到您要投票的人\n\n请尽量保持文字正确哦。 >^<n\n请您继续投杀死  ->白芷莳<-- 的凶手")

        elif stage == 5:
            r = self.game.cm.predictCertainly(textboxValue)
            if r == 'true':
                words = self.game.review()
                self.myPrint(words)
                self.currentVoicePath = 'resources/Sound/review.wav'
                self.playVoice.start(1000)
            else:
                self.myPrint("准备好进入复盘阶段请告诉我")

        self.textbox.setText('')


    #function
    def play(self, filename):
        self.playVoice.stop()
        chunk = 1024  # 2014kb
        wf = wave.open(filename, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                        rate=wf.getframerate(), output=True)

        while True:
            data = wf.readframes(chunk)
            # print(data)
            if data == b'':
                break
            stream.write(data)
        stream.stop_stream()  # 停止数据流
        stream.close()
        p.terminate()  # 关闭 PyAudio


    def clearScreen(self):
        self.textbox2.setText('')


class GameLogic():
    def __init__(self):

        # params
        jieba.load_userdict("src/myWords.txt")

        self.recordFace = {'zhang': False,
                      'luo': False,
                      'chen': False,
                      'wu': False,
                      'sun': False,
                      'lin': False}

        self.startTimes = 0

        self.MeanDict = {0: 'clear',
                         1: 'vague'}

        # self.nagative = ['不', '没', '无', '别']
        # self.positive = ['好', '行', '妥', '哦', '嗯', '恩', '是']

        # 初始阶段 章乔 罗宇飞 陈兴元 吴有为 孙云业 林夺
        self.currentMessage1 = {'zhang': 1, 'luo': 1, 'chen': 1, 'wu': 1, 'sun': 1, 'lin': 1, 'school': 1, 'body': 1,
                                'other': 1}
        self.currentMessage2 = {'zhang': 1, 'luo': 1, 'chen': 1, 'wu': 1, 'sun': 1, 'lin': 1, 'school': 1, 'body': 1,
                                'other': 1}
        self.currentMessage3 = {'zhang': 1, 'luo': 1, 'chen': 1, 'wu': 1, 'sun': 1, 'lin': 1, 'school': 1, 'body': 1,
                                'other': 1}

        # 获得的线索列表
        self.zhang = []
        self.luo = []
        self.chen = []
        self.wu = []
        self.sun = []
        self.lin = []
        self.nameDict = {'zhang': self.zhang,
                         'luo': self.luo,
                         'chen': self.chen,
                         'wu': self.wu,
                         'sun': self.sun,
                         'lin': self.lin
                         }
        # 匹配几条线索的 正则
        self.xs = re.compile(r'.*([0-9]+).*?线索')
        # 游戏存档
        self.dictSave = {}
        # 当前状态是否可以退回
        self.enable = True

        self.nameMap = {'zhang': '章乔',
                        'luo': '罗宇飞',
                        'chen': '陈兴元',
                        'wu': '吴有为',
                        'sun': '孙云业',
                        'lin': '林夺'
                        }

        self.nameMapForLabel = {'zhang': '章乔',
                        'luo': '罗宇飞',
                        'chen': '陈兴元',
                        'wu': '吴有为',
                        'sun': '孙云业',
                        'lin': '林夺',
                        'deep':'深入线索',
                        'special':'特殊线索',
                        'body':'案发现场',
                        'other':'其他区域',
                        'school':'学校周边'
                        }

        self.messageLeft1 = {'zhang': 3, 'luo': 3, 'chen': 3, 'wu': 3, 'sun': 3, 'lin': 3}
        self.messageLeft2 = {'zhang': 3, 'luo': 3, 'chen': 3, 'wu': 3, 'sun': 3, 'lin': 3}
        self.messageLeft3 = {'zhang': 3, 'luo': 3, 'chen': 3, 'wu': 3, 'sun': 3, 'lin': 3}

        self.maxMessage1 = {'zhang': 2, 'luo': 2, 'chen': 2, 'wu': 2, 'sun': 2, 'lin': 2,'school':2,'other':1,'body':3}
        self.maxMessage2 = {'zhang': 2, 'luo': 2, 'chen': 2, 'wu': 2, 'sun': 2, 'lin': 2,'school':2,'other':1,'body':3}
        self.maxMessage3 = {'zhang': 2, 'luo': 1, 'chen': 2, 'wu': 1, 'sun': 2, 'lin': 2,'school':1,'other':3,'body':1}


        self.voted = {'zhang': 0, 'luo': 0, 'chen': 0, 'wu': 0, 'sun': 0, 'lin': 0}
        self.doVote = {'zhang': None, 'luo': None, 'chen': None, 'wu': None, 'sun': None, 'lin': None}

        self.voted2 = {'zhang': 0, 'luo': 0, 'chen': 0, 'wu': 0, 'sun': 0, 'lin': 0}
        self.doVote2 = {'zhang': None, 'luo': None, 'chen': None, 'wu': None, 'sun': None, 'lin': None}

        self.currentStage = -1
        # # game
        # s1 = self.stage1Init()
        # s2 = self.stage2Init()
        #
        # vote = self.voteInit()
        # review = self.review()
        # self.stages = [s1, s2, vote, review]

        # model
        # 初始化模型
        self.fr = fm.FaceRecognition()
        self.cm = certainlyModel.CertainlyModel()
        self.am = actionModel.ActionModel()

        #special Message for game
        self.password = '050512'
        self.passwordPreMessage = "wu/2/1.jpg"
        self.passwordName = ""
        self.passwordLeft = 3

        self.specialPreMessage = "body/1/2.jpg"

        self.preMessagePath4DeepMessage = {
            'body':'../juben/resources/Message/body/2/3.jpg',
            'luo':'../juben/resources/Message/luo/1/2.jpg',
            'wu':'../juben/resources/Message/wu/1/1.jpg'
        }
        self.deepMessage = {
            'body':'../juben/resources/Message/deep/body.jpg',
            'luo':'../juben/resources/Message/deep/luo.jpg',
            'wu':'../juben/resources/Message/deep/wu.jpg'
        }

        self.computerAndUdisk = False

    def getStartTimes(self):
        return self.startTimes

    def increaseStartTimes(self):
        self.startTimes += 1


    def getUnrecordList(self):
        return [self.nameMap[k] for k, v in self.recordFace.items() if not v]

    def getPwd(self):
        return self.password

    def resetEnable(self):
        self.enable = True

    def getEnable(self):
        return self.enable

    def getCurrentStage(self):
        return self.currentStage

    def nextStage(self):
        self.currentStage += 1

    def previousStage(self):
        self.currentStage -= 1

    def findPlace(self, sent):
        if '章' in sent or '乔' in sent:
            return 'zhang'
        elif '罗' in sent or '宇飞' in sent:
            return 'luo'
        elif '陈' in sent or '兴元' in sent:
            return 'chen'
        elif '吴' in sent or '有为' in sent:
            return 'wu'
        elif '孙' in sent or '云业' in sent:
            return 'sun'
        elif '林' in sent or '夺' in sent:
            return 'lin'
        elif '校园' in sent or '周边' in sent:
            return 'school'
        elif '其他' in sent:
            return 'other'
        elif '现场' in sent:
            return 'body'
        else:
            return 'vague'

    def findName(self, sent):
        if '章' in sent or '乔' in sent:
            return 'zhang'
        elif '罗' in sent or '宇飞' in sent:
            return 'luo'
        elif '陈' in sent or '兴元' in sent:
            return 'chen'
        elif '吴' in sent or '有为' in sent:
            return 'wu'
        elif '孙' in sent or '云业' in sent:
            return 'sun'
        elif '林' in sent or '夺' in sent:
            return 'lin'
        else:
            return 'vague'

    def getChineseName(self, name):
        return self.nameMap.get(name)

    def findNum(self, sent):
        sent = sent.replace('一', '1')
        sent = sent.replace('壹', '1')

        sent = sent.replace('二', '2')
        sent = sent.replace('两', '2')
        sent = sent.replace('贰', '2')

        sent = sent.replace('三', '3')
        sent = sent.replace('仨', '3')
        sent = sent.replace('叁', '3')

        sent = sent.replace('四', '4')
        sent = sent.replace('肆', '4')

        sent = sent.replace('五', '5')
        sent = sent.replace('伍', '5')

        sent = sent.replace('六', '6')
        sent = sent.replace('陆', '6')

        sent = sent.replace('七', '7')
        sent = sent.replace('柒', '7')

        sent = sent.replace('八', '8')
        sent = sent.replace('捌', '8')

        sent = sent.replace('九', '9')
        sent = sent.replace('玖', '9')

        sent = sent.replace('零', '0')

        sent = sent + "线索"
        return self.xs.findall(sent)

    def findKillerList(self):
        killerList = []
        voteNum = 0
        for key, value in self.voted.items():
            if value > voteNum:
                killerList = []
                killerList.append(key)
                voteNum = value
            elif value == voteNum:
                killerList.append(key)
            else:
                continue
        return killerList

    def findKillerList2(self):
        killerList = []
        voteNum = 0
        for key, value in self.voted2.items():
            if value > voteNum:
                killerList = []
                killerList.append(key)
                voteNum = value
            elif value == voteNum:
                killerList.append(key)
            else:
                continue
        return killerList

    def getLeftMessage(self):
        if self.getCurrentStage() == 1:
            words = "当前剩余线索:\n" + " 章乔：%d 条\n 罗宇飞：%d 条\n 陈兴元：%d 条\n 吴有为：%d 条\n 孙云业：%d 条\n 林夺：%d 条\n 校园周边：%d 条\n 案发现场：%d 条\n 其他地方：%d 条\n" % (
        (self.maxMessage1['zhang'] - self.currentMessage1['zhang'] + 1), (self.maxMessage1['luo'] - self.currentMessage1['luo'] + 1),
        (self.maxMessage1['chen'] - self.currentMessage1['chen'] + 1), (self.maxMessage1['wu'] - self.currentMessage1['wu'] + 1),
        (self.maxMessage1['sun'] - self.currentMessage1['sun'] + 1), (self.maxMessage1['lin'] - self.currentMessage1['lin'] + 1),
        (self.maxMessage1['school'] - self.currentMessage1['school'] + 1), (self.maxMessage1['body'] - self.currentMessage1['body'] + 1),
        (self.maxMessage1['other'] - self.currentMessage1['other'] + 1))
            return words
        elif self.getCurrentStage() == 2:
            words = "当前剩余线索:\n" + " 章乔：%d 条\n 罗宇飞：%d 条\n 陈兴元：%d 条\n 吴有为：%d 条\n 孙云业：%d 条\n 林夺：%d 条\n 校园周边：%d 条\n 案发现场：%d 条\n 其他地方：%d 条\n" % (
        (self.maxMessage2['zhang'] - self.currentMessage2['zhang'] + 1), (self.maxMessage2['luo'] - self.currentMessage2['luo'] + 1),
        (self.maxMessage2['chen'] - self.currentMessage2['chen'] + 1), (self.maxMessage2['wu'] - self.currentMessage2['wu'] + 1),
        (self.maxMessage2['sun'] - self.currentMessage2['sun'] + 1), (self.maxMessage2['lin'] - self.currentMessage2['lin'] + 1),
        (self.maxMessage2['school'] - self.currentMessage2['school'] + 1), (self.maxMessage2['body'] - self.currentMessage2['body'] + 1),
        (self.maxMessage2['other'] - self.currentMessage2['other'] + 1))
            return words
        elif self.getCurrentStage() == 3:
            words = "当前剩余线索:\n" + " 章乔：%d 条\n 罗宇飞：%d 条\n 陈兴元：%d 条\n 吴有为：%d 条\n 孙云业：%d 条\n 林夺：%d 条\n 校园周边：%d 条\n 案发现场：%d 条\n 其他地方：%d 条\n" % (
        (self.maxMessage3['zhang'] - self.currentMessage3['zhang'] + 1), (self.maxMessage3['luo'] - self.currentMessage3['luo'] + 1),
        (self.maxMessage3['chen'] - self.currentMessage3['chen'] + 1), (self.maxMessage3['wu'] - self.currentMessage3['wu'] + 1),
        (self.maxMessage3['sun'] - self.currentMessage3['sun'] + 1), (self.maxMessage3['lin'] - self.currentMessage3['lin'] + 1),
        (self.maxMessage3['school'] - self.currentMessage3['school'] + 1), (self.maxMessage3['body'] - self.currentMessage3['body'] + 1),
        (self.maxMessage3['other'] - self.currentMessage3['other'] + 1))
            return words

    def SearchDeepMessageByPremessage(self,name):
        deeplist = []
        print("所有线索",self.nameDict.get(name))
        print("深入案发现场线索", self.preMessagePath4DeepMessage.get('body'))
        print("深入罗线索", self.preMessagePath4DeepMessage.get('luo'))
        print("深入吴线索", self.preMessagePath4DeepMessage.get('wu'))
        if self.preMessagePath4DeepMessage.get('body') in self.nameDict.get(name):
            deeplist.append(self.deepMessage.get('body'))
        if self.preMessagePath4DeepMessage.get('luo') in self.nameDict.get(name):
            deeplist.append(self.deepMessage.get('luo'))
        if self.preMessagePath4DeepMessage.get('wu') in self.nameDict.get(name):
            deeplist.append(self.deepMessage.get('wu'))
        print(name,"'s deeplist:",deeplist)
        return deeplist

    def goDeep(self, searchDict, name):
        #只有第二轮第三轮能搜查
        if self.getCurrentStage() == 2 or self.getCurrentStage() == 3:
            if self.getCurrentStage() == 2:
                messageLeft = self.messageLeft2
            else:
                messageLeft = self.messageLeft3

            if messageLeft.get(name) > 0:
                if searchDict is None:
                    #说深入调查 没说调查谁
                    able2SearchDeepList = self.SearchDeepMessageByPremessage(name)
                    print(name,'可以调查',str(len(able2SearchDeepList)),'条深入线索')
                    if len(able2SearchDeepList) == 0:
                        return 'noPreMessage'
                    elif len(able2SearchDeepList) == 1:
                        if able2SearchDeepList[0] not in self.nameDict.get(name):
                            self.nameDict.get(name).append(able2SearchDeepList[0])
                            if self.getCurrentStage() == 2:
                                self.messageLeft2[name] = messageLeft.get(name) - 1
                            else:
                                self.messageLeft3[name] = messageLeft.get(name) - 1
                            return able2SearchDeepList[0]
                        else:
                            return 'alreadyHave'
                    else:
                        return 'deepSearchNoPerson'
                else:
                    #说了搜谁的深入线索
                    if searchDict['place'] == 'wu' or searchDict['place'] == 'body' or searchDict['place'] == 'luo':
                        #这三个人有，可以查
                        if self.preMessagePath4DeepMessage.get(searchDict['place']) in self.nameDict.get(name):
                            if self.deepMessage.get(searchDict['place']) not in self.nameDict.get(name):
                                self.nameDict.get(name).append(self.deepMessage.get(searchDict['place']))
                                if self.getCurrentStage() == 2:
                                    self.messageLeft2[name] = messageLeft.get(name) - 1
                                else:
                                    self.messageLeft3[name] = messageLeft.get(name) - 1
                                return self.deepMessage.get(searchDict['place'])
                            else:
                                return 'alreadyHave'
                        else:
                            return 'noPreMessage'
                    else:
                        return 'noDeepForPerson'
            else:
                return 'notEnoughMessage'
        else:
            return 'IncorrectStage'



    def ownMessage(self, name):
        ownList = []
        if len(self.nameDict[name]) == 0:
            return "您尚未拥有线索"
        else:
            for i in self.nameDict[name]:
                if i.endswith(".jpg"):
                    ownList.append(i)
            return ownList

    def doSearch(self, searchDict, name):

        searchList = []
        if self.currentStage == 1:
            maxMessage, messageLeft, currentMessage = self.maxMessage1, self.messageLeft1, self.currentMessage1
        elif self.currentStage == 2:
            maxMessage, messageLeft, currentMessage = self.maxMessage2, self.messageLeft2, self.currentMessage2
        elif self.currentStage == 3:
            maxMessage, messageLeft, currentMessage = self.maxMessage3, self.messageLeft3, self.currentMessage3
        else:
            print("搜查 但是第四阶段")
            return '当前回合无法搜查'

        # 获取对应人的信息
        place = searchDict['place']
        num = searchDict['num'][0]  # 正则返回的是列表



        try:
            num = int(num)
        except Exception as e:
            print('抱歉请使用阿拉伯数字')
            return "抱歉请使用阿拉伯数字"

        # 每一个地方只有三个线索
        if num > 3:
            num = 3

        ml = messageLeft[name]
        cm = currentMessage[place]
        mm = maxMessage[place]
        extra_message = None
        # 搜查数量剩余1条，想要2条就只给1条就行了
        while ml > 0 and num > 0:  # 可以进行搜查
            # 如果还有剩余线索
            if mm >= cm:
                messagePicPath = '../juben/resources/Message/' + place + '/' + str(self.currentStage) + '/' + '%d' % cm + '.jpg'
                #messagePath = '../juben/resources/Message/' + place + '/' + str(self.currentStage) + '/' + '%d' % cm
                searchList.append(messagePicPath)
                # 搜查过了，不能返回了
                self.enable = False
                # 剩余搜查的线索-1
                num = num - 1
                # 剩余线索-1
                ml = ml - 1
                # 当前线索+1
                cm = cm + 1
                # 将该条线索记录至当前玩家的已搜查列表
                self.nameDict[name].append(messagePicPath)
                #self.nameDict[name].append(messagePath)
                if self.specialPreMessage in messagePicPath:
                    self.computerAndUdisk = True
                if self.passwordPreMessage in messagePicPath:
                    self.passwordName = name

                time.sleep(0.2)
                if num == 0:
                    break
            else:
                extra_message = "该场景的线索已经被搜完\n"
                break
        else:
            extra_message = "您可搜查的线索数量已经不足，每人每回合三条\n"

        if self.currentStage == 1:
            self.messageLeft1[name], self.currentMessage1[place] = ml, cm
        elif self.currentStage == 2:
            self.messageLeft2[name], self.currentMessage2[place] = ml, cm
        else:
            self.messageLeft3[name], self.currentMessage3[place] = ml, cm

        messageLeft[name], currentMessage[place] = ml, cm

        words = extra_message

        return words,searchList

    def detectFace(self):
        # 做声音的检查，现在没有声音，
        name = self.fr.predictFace(6)
        if name == 'vague':
            return self.detectFace()
        print('你好', self.nameMap[name])
        return name

    # def getUserInput(self):
    #     while True:
    #         self.message = self.ex.getMessage()
    #         if self.message != None:
    #             self.ex.copyThat()
    #         time.sleep(0.1)

    def predictAction(self, sent):
        if self.am.predictAction(sent) == 'next':
            return "next", None

        elif self.am.predictAction(sent) == 'own':
            return 'own', None

        elif self.am.predictAction(sent) == 'search':

            # # 只进行深入调查
            # if '深' in sent or 'A' in sent or 'B' in sent or 'C' in sent or 'D' in sent or 'E' in sent:
            #     return 'deep',key

            # 定义一个搜查的字典  key：place/num
            searchDict = {'place': 'vague', 'num': []}
            num = self.findNum(sent)
            place = self.findPlace(sent)
            searchDict['num'] = num
            searchDict['place'] = place
            if searchDict['place'] == 'vague' and searchDict['num'] == []:
                return 'searchNoPerson', None

            elif searchDict['place'] != 'vague' and searchDict['num'] == []:
                return 'searchNoNum', searchDict
                # k = input("请告诉我你想要搜查的线索数量\n")
                # num = self.findNum(k)
                # if num != []:
                #     searchDict['num'] = num
                #     messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage, stage1.__name__, name)
                #     return 'nothing'
                # else:
                #     print("对不起，未能识别数量，请用中文汉字或阿拉伯数字")

            elif searchDict['place'] == 'vague' and searchDict['num'] != []:
                return 'searchNoPerson', searchDict
                # k = input("请告诉我你想要搜查的地方\n")
                # place = self.findPlace(k)
                # if place != 'vague':
                #     searchDict['place'] = place
                #     messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage, stage1.__name__, name)
                #     return 'nothing'
                # else:
                #     print("对不起,未能识别地点，请说的清楚一些")
                #     return 'nothing'
            else:
                # messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage, stage1.__name__, name)
                return 'search', searchDict
        elif self.am.predictAction(sent) == 'previous':
            return "previous", None
        else:
            return "vague", None

    def review(self):
        word = "我是陈兴元，不，或者说该叫我孙义兢。我是云业的哥哥。十四年前，我姐姐孙漓怀揣着梦想考入了公州大学，成为了医学系的研究生。她不光年轻貌美，学习上也是出类拔萃" \
               "然而，却爱上了一个叫宁国的渣男。有一次姐姐跟吴有为聊天时谈到，她怀了宁国的孩子，而宁国也答应她毕业之后就结婚。一切都是这么完美，吴有为在嫉妒宁国的同时，也祝福着姐姐。" \
               "但姐姐的论文发表了，署名却只有宁国。宁国结婚了，新娘却不是姐姐。更可恶的是，宁国居然还到处散布谣言，诬陷姐姐勾三搭四，企图洗白自己。当我知道真相的时候，暗下决心，一定要为姐姐复仇。" \
               "随后我便找弟弟帮我安排了一份给医学院搬送货物的工作，工作中我认识了林夺。她也是一个可怜的人，可能是同病相怜吧？我对她产生了好感，她对我也毫无保留。一次跟她聊天中，她竟然告诉我" \
               "她来到学校就是为了杀死白芷莳。因为宁国告诉她，当年导致她女儿医疗意外死亡的罪魁祸首，就是白芷莳！看过弟弟侦探小说的我不由得心生一计：交换杀人！为对方洗脱动机的嫌疑。" \
               "林夺提前观察了宁国的生活习惯，偷取了实验室的氰化钾粉末，今天，她看见宁国拎着早餐走进办公室后，便将氰化钾撒在了宁国习惯使用的擦手纸上面，毒死了他。8：45她遥控宁国哼歌的录音笔，企图混淆宁国的死亡时间。" \
               "知道她得手后，10：45我偷偷去了天台，将我用弟弟手机约来的白芷莳用乙醚迷晕，并关上了天台门，11点我将白芷莳拖到天台边，摆成坐着的样子。拿出提前准备好的鱼线轮和鱼钩，用结实的鱼钩勾住了白芷莳的衣服，" \
               "把鱼线拉出固定在天台的侧把手上。绷直的鱼线刚好作为她往下倾的支撑。布置好后，锁上了天台，将新配的天台钥匙扔进附近的草丛，制造其他人复制钥匙的假象，并用白芷莳的手机群发了一条短信'我真的厌倦了这个世界'，" \
               "发送时间定为12点。当所有人冲向天台，撞门无果。身为主角的我最后出场，拿出钥匙，送了白芷莳最后一程。'再见，为了报仇，你也必须死。' " \
               "我欣赏着自己完美的计划，姐姐，我终于给你报仇了！\n" \
               "所有的杀戮都是一场华丽的演出，而我的演出，没有人能缺席，演出结束，帷幕落下。有些假象足以把人钉在十字架上，可以忏悔，但无法解脱。\n\n" \
               "各位如果想看具体的证据卡解释，请压缩包内查找"

        return word

    def vote(self,votedName,doName):
        print("请玩家投票")
        if votedName != 'vague' and doName != 'vague' and self.doVote.get(doName) is None:
            self.enable = False
            self.voted[votedName] += 1
            self.doVote[doName] = True
        return [self.nameMap.get(key) for key,value in self.doVote.items() if value is None]

    def vote2(self,votedName,doName):
        print("请玩家投票")
        if votedName != 'vague' and doName != 'vague' and self.doVote2.get(doName) is None:
            self.voted2[votedName] += 1
            self.doVote2[doName] = True
        return [self.nameMap.get(key) for key,value in self.doVote2.items() if value is None]

    def prepareVote2(self,killerList):
        #发起来第二轮投票
        voteList2 = []
        #将没有投票得票最多的人的人选出
        for key,value in self.doVote.items():
            if value not in killerList:
                #将这些人的投票结果清空
                self.doVote[key] = None
                voteList2.append(key)
        return voteList2

    # def stage1Init(self,messageLeft={'zhang':3,'luo':3,'chen':3,'wu':3,'sun':3,'lin':3},maxMessage={'zhang':3,'luo':3,'chen':3,'wu':3,'sun':3,'lin':3},currentMessage={'zhang':1,'luo':1,'chen':1,'wu':1,'sun':1,'lin':1}):
    #     def stage1(self,*args,**kw):
    #         nonlocal messageLeft,maxMessage #修改外部变量的时候
    #         #print(messageLeft)
    #
    #         while True:
    #             #等待玩家说进入第二轮，或者搜查
    #             #time.sleep(2)
    #
    #             self.ex.myPrint("现在可搜查线索\n")
    #             self.ex.myPrint('章乔剩余', maxMessage['zhang'] - self.currentMessage['zhang'] + 1, '条线索\n')
    #             self.ex.myPrint('罗宇飞剩余', maxMessage['luo'] - self.currentMessage['luo'] + 1, '条线索\n')
    #             self.ex.myPrint('陈兴元剩余', maxMessage['chen'] - self.currentMessage['chen'] + 1, '条线索\n')
    #             self.ex.myPrint('吴有为剩余', maxMessage['wu'] - self.currentMessage['wu'] + 1, '条线索\n')
    #             self.ex.myPrint('孙云业剩余', maxMessage['sun'] - self.currentMessage['sun'] + 1, '条线索\n')
    #             self.ex.myPrint('林夺剩余', maxMessage['lin'] - self.currentMessage['lin'] + 1, '条线索\n')
    #
    #             self.ex.myPrint("注意每一次搜查，只能搜查一个人!\n下面请告诉我你想做的事情\n提示：现在我们可以去调查别人的线索，查看自己有的线索，也可以进入下个阶段\n")
    #
    #             sent = input("")
    #
    #
    #     return stage1
    #
    #
    # def stage2Init(self, messageLeft={'zhang':3,'luo':3,'chen':3,'wu':3,'sun':3,'lin':3}, maxMessage={'zhang':3,'luo':3,'chen':3,'wu':3,'sun':3,'lin':3}):
    #     def stage2(self, *args, **kw):
    #         nonlocal messageLeft,maxMessage  # 修改外部变量的时候
    #         #print(messageLeft)
    #         #enable 能否返回上一阶段的标识符
    #         self.enable = True
    #
    #         str = "那么现在第二轮搜查正式开始\n若误操作进入第二阶段，任何玩家还未搜查的情况下，可以要求我，返回上一阶段\n\n"
    #         self.myPrint(str)
    #         while True:
    #             # 等待玩家说进入第二轮，或者搜查
    #             #time.sleep(2)
    #             print()
    #             print("现在可搜查线索")
    #             print('尸体剩余', maxMessage['body'] - self.currentMessage['body'] + 1, '条线索')
    #             print('林教授剩余', maxMessage['professor'] - self.currentMessage['professor'] + 1, '条线索')
    #             print('阿海剩余', maxMessage['hai'] - self.currentMessage['hai'] + 1, '条线索')
    #             print('老板娘剩余', maxMessage['host'] - self.currentMessage['host'] + 1, '条线索')
    #             print('杜助理剩余', maxMessage['du'] - self.currentMessage['du'] + 1, '条线索')
    #             print('刘编辑剩余', maxMessage['liu'] - self.currentMessage['liu'] + 1, '条线索')
    #             print('漫画家公寓剩余', maxMessage['cartoonist'] - self.currentMessage['cartoonist'] + 1, '条线索')
    #             print()
    #             sent = input("注意每一次搜查，只能搜查一个人!\n下面请告诉我你想做的事情\n")
    #
    #             if self.am.predictAction(sent) == 'next':
    #                 sure = input("确认后本轮搜查结束，所有玩家将进入下一阶段，请问是否确认\n")
    #                 if self.cm.predictCertainly(sure) == 'true':
    #                     # 进入下一轮 ，那么返回游戏结果的字典
    #                     return 'next'
    #                 else:
    #                     print('不进入投票的话，那我们继续这轮搜查吧')
    #                     continue
    #             elif self.am.predictAction(sent) == 'previous':
    #                 if self.enable:
    #                     sure = input("确认后，所有玩家将返回上一阶段，请问是否确认\n")
    #                     if self.cm.predictCertainly(sure) == 'true':
    #                         #???????这里跟游戏流程的for循环有关，for循环也要退回一次
    #                         return 'previous'
    #                 else:
    #                     print("已经有玩家搜查了线索，无法返回")
    #                     continue
    #
    #             elif self.am.predictAction(sent) == 'own':
    #                 name = self.detectFace()
    #                 self.ownMessage(name)
    #
    #             elif self.am.predictAction(sent) == 'search':
    #
    #                 # 识别sent是哪个人
    #                 name = self.detectFace()
    #
    #                 # 这块应该永远不会是vague因为是vague无法返回，回调了
    #                 if name == 'vague':
    #                     # 不能识别的名字,重新输入指令
    #                     continue
    #
    #                 # 定义一个搜查的字典  key：place/num
    #                 searchDict = {'place': 'vague', 'num': []}
    #                 num = self.findNum(sent)
    #                 place = self.findPlace(sent)
    #                 searchDict['num'] = num
    #                 searchDict['place'] = place
    #
    #                 # 只进行深入调查
    #                 if ('深' in sent or 'A' in sent or 'B' in sent or 'C' in sent or 'D' in sent or 'E' in sent) and \
    #                         searchDict['place'] == 'vague':
    #                     messageLeft = self.goDeep(sent, messageLeft, name)
    #                     continue
    #
    #                 if searchDict['place'] == 'vague' and searchDict['num'] == []:
    #                     print('对不起，未能识别，请告诉我你想做的事情')
    #                     continue
    #                 elif searchDict['place'] != 'vague' and searchDict['num'] == []:
    #                     k = input("请告诉我你想要搜查的线索数量\n")
    #                     num = self.findNum(k)
    #                     if num != []:
    #                         searchDict['num'] = num
    #                         messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage,
    #                                                                                 stage2.__name__, name)
    #                         continue
    #                     else:
    #                         k = input("对不起，未能识别数量，请用中文汉字或阿拉伯数字\n")
    #                         num = self.findNum(k)
    #                         if num != []:
    #                             searchDict['num'] = num
    #                             messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage,
    #                                                                     stage2.__name__, name)
    #                             continue
    #                         else:
    #                             print("抱歉依然未能识别，请重新输入命令")
    #                             continue
    #                 elif searchDict['place'] == 'vague' and searchDict['num'] != []:
    #                     k = input("请告诉我你想要搜查的地方\n")
    #                     place = self.findPlace(k)
    #                     if place != 'vague':
    #                         searchDict['place'] = place
    #                         messageLeft, maxMessage = self.doSearch(searchDict, messageLeft,
    #                                                                                 maxMessage,
    #                                                                                 stage2.__name__, name)
    #                         continue
    #                     else:
    #                         print("对不起,未能识别地点，请说的清楚一些")
    #                         continue
    #                 else:
    #                     messageLeft, maxMessage = self.doSearch(searchDict, messageLeft, maxMessage,
    #                                                                             stage2.__name__, name)
    #                     continue
    #             else:
    #                 print("请告诉我你想做的事情")
    #                 continue
    #
    #     return stage2
    #
    #
    # def voteInit(self,voted={'professor':0,'hai':0,'liu':0,'host':0,'du':0},doVote={'professor':None,'hai':None,'liu':None,'host':None,'du':None,'detective':None}):
    #     def vote(self,*args,**kw):
    #         nonlocal voted, doVote
    #         print('本轮为投票阶段，玩家无法搜查线索，请根据已有线索进行讨论。\n推断作案动机和手法 ,并告诉我你认为谁是凶手，被投票最多的玩家出局\n若平票，则未投该玩家的玩家进行二次投票')
    #         print('若误操作进入投票阶段，可以告诉我，我们可以返回上一个阶段')
    #
    #         numLoop = 0
    #
    #         while numLoop < len(doVote):
    #
    #             #打印已投票玩家
    #             nl = [self.nameMap[k] for k, v in doVote.items() if v is not None]
    #             print("已投票玩家: ",' '.join(nl))
    #
    #             words = input('请告诉我，你认为谁是凶手\n')
    #             do_name = self.detectFace()
    #
    #             killer = self.findName(words)
    #             if killer != 'vague' and killer != 'detective':
    #
    #                 sure = input('确认投票 %s 为凶手么？\n'%self.nameMap[killer])
    #                 if self.cm.predictCertainly(sure) == 'true':
    #                     if doVote[do_name] == None:
    #                         voted[killer] = voted[killer] + 1
    #                         doVote[do_name] = killer
    #                         numLoop = numLoop + 1
    #                         print('投票成功')
    #                     else:
    #                         print('您已投票，无法再次投票')
    #                 else:
    #                     print('投票已取消')
    #                     continue
    #             else:
    #                 print('抱歉，未能识别改名字，请更加准确一些')
    #
    #         #第一轮完成，找出最多的同票玩家
    #         killerList = []
    #         voteNum = 0
    #         for key,value in voted.items():
    #             if value > voteNum:
    #                 killerList = []
    #                 killerList.append(key)
    #                 voteNum = value
    #             elif value == voteNum:
    #                 killerList.append(key)
    #             else:
    #                 continue
    #         #print(voted)
    #
    #         if len(killerList) == 1:
    #             # 被投票最多的凶手
    #             names2 = []
    #             for i in killerList:
    #                 names2.append(self.nameMap[i])
    #             print('投票凶手为:', ' '.join(names2))
    #         else:
    #             #发起来第二轮投票
    #             voteList2 = []
    #             doVote2 = doVote
    #             #将没有投票得票最多的人的人选出
    #             for key,value in doVote.items():
    #                 if value not in killerList:
    #                     #将这些人的投票结果清空
    #                     doVote2[key] = None
    #                     voteList2.append(key)
    #             #再次投票的玩家
    #             names = []
    #             for i in voteList2:
    #                 names.append(self.nameMap[i])
    #             #被投票最多的凶手
    #             names2 = []
    #             for i in killerList:
    #                 names2.append(self.nameMap[i])
    #
    #             print("请未投",' '.join(names2),"的玩家\n",' '.join(names),'选择其中一个进行投票')
    #             if len(voteList2) == 0:
    #                 print("平票，凶手获胜")
    #
    #
    #             numLoop = 0
    #
    #             while numLoop < len(voteList2):
    #
    #                 # 打印已投票玩家
    #                 # print("已投票玩家：", end='')
    #                 # for key, value in doVote.items():
    #                 #     if value is not None:
    #                 #         print(self.nameMap[key], ' ',end='')
    #                 # print()
    #                 # 打印已投票玩家
    #                 nl = [self.nameMap[k] for k, v in doVote.items() if v is not None]
    #                 print("已投票玩家: ", ' '.join(nl))
    #
    #                 words = input('请告诉我，你认为谁是凶手\n')
    #                 do_name = self.detectFace()
    #
    #                 killer = self.findName(words)
    #                 if killer in killerList:
    #
    #                     sure = input('确认投票 %s 为凶手么？\n' % self.nameMap[killer])
    #                     if self.cm.predictCertainly(sure) == 'true':
    #                         if doVote2[do_name] == None:
    #                             voted[killer] = voted[killer] + 1
    #                             doVote2[do_name] = killer
    #                             numLoop = numLoop + 1
    #                             print('投票成功')
    #                         else:
    #                             print('您已投票，无法再次投票')
    #                     else:
    #                         print('投票已取消')
    #                         continue
    #                 else:
    #                     print('抱歉，只能投给',' '.join(names2))
    #
    #                 # 第二轮完成，找出最多的同票玩家
    #                 killerList = []
    #                 voteNum = 0
    #                 for key, value in voted.items():
    #                     if value > voteNum:
    #                         killerList = []
    #                         killerList.append(key)
    #                         voteNum = value
    #                     elif value == voteNum:
    #                         killerList.append(key)
    #                     else:
    #                         continue
    #
    #                 #print(voted)
    #                 # 被投票最多的凶手
    #                 names2 = []
    #                 for i in killerList:
    #                     names2.append(self.nameMap[i])
    #                 print('投票凶手为:',' '.join(names2))
    #     return vote
    #
    #
    # def review(self):
    #     def story(self,*arg,**kw):
    #         print("这里是复盘")
    #
    #     return story
    #
    # def gameCertainlyed(self):
    #
    #     i = 0
    #     while i < len(self.stages):
    #         command = self.stages[i](self)
    #         if command == 'previous':
    #             i = i - 1
    #         else:
    #             i = i + 1
    #
    #     print('游戏结束')


if __name__ == '__main__':





    app = QApplication(sys.argv)

    game = GameLogic()
    ex = GameUi(game)

    ex.window()
    ex.prestart('')
    #ex.open_camera()

    #game.showImg()
    sys.exit(app.exec_())
