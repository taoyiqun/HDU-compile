import sys
from PyQt5.QtWidgets import QWidget, \
    QPushButton, \
    QToolTip, \
    QMessageBox, \
    QApplication, \
    QDesktopWidget, \
    QMainWindow, \
    QAction, \
    qApp, \
    QLCDNumber, \
    QSlider, \
    QVBoxLayout, \
    QHBoxLayout, QTableWidget, QTextBrowser, QTextEdit, QLabel, QAbstractItemView, QTableWidgetItem, QLineEdit, \
    QHeaderView
from PyQt5.QtCore import Qt, \
    QObject, \
    pyqtSignal
from PyQt5.QtGui import QFont, \
    QIcon, QBrush, QColor
from PyQt5.uic.properties import QtGui, QtWidgets

import Util
class Communicate(QObject):
    closeApp = pyqtSignal()


# QMainWindow是QWidget的派生类
class CMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.table_widget =  QTableWidget()
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.Browser = QTextBrowser()
        self.label = QLabel()
        self.Edit = QTextEdit()

        # ToolTip设置
        QToolTip.setFont(QFont('宋体', 15))

        # statusBar设置
        self.statusBar().showMessage('准备就绪')

        # 退出Action设置
        oneAction = QAction('&开始', self)
        oneAction.setShortcut('ctrl+Q')
        oneAction.setStatusTip('词法分析')
        oneAction.triggered.connect(self.Lex)  # qApp就相当于QCoreApplication.instance()
        twoAction = QAction('&递归向下', self)
        twoAction.setShortcut('ctrl+T')
        twoAction.setStatusTip('语法分析')
        twoAction.triggered.connect(self.parse)  # qApp就相当于QCoreApplication.instance()
        threeAction = QAction( '&分析表', self)
        threeAction.setShortcut('ctrl+V')
        threeAction.setStatusTip('LL1语法分析')
        threeAction.triggered.connect(self.gettable)  # qApp就相当于QCoreApplication.instance()
        fourAction = QAction('&分析过程', self)
        fourAction.setShortcut('ctrl+X')
        fourAction.setStatusTip('LL1语法分析')
        fourAction.triggered.connect(self.getprocess)  # qApp就相当于QCoreApplication.instance()
        fiveAction = QAction('&优化后的产生式', self)
        fiveAction.setShortcut('ctrl+K')
        fiveAction.setStatusTip('LL1语法分析')
        fiveAction.triggered.connect(self.funleft)  # qApp就相当于QCoreApplication.instan
        # menuBar设置
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&词法分析')
        fileMenu.addAction(oneAction)
        twoMenu=menubar.addMenu('&语法分析')
        twoMenu.addAction(twoAction)
        twoMenu.addAction(threeAction)
        twoMenu.addAction(fourAction)
        twoMenu.addAction(fiveAction)
        # table设置
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        horizontalLayout =QHBoxLayout()
        horizontalLayout.addWidget( self.table_widget)
        self.Browser.setFont(QFont('Consolas',20))
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.Browser)
        self.label.setText('源码')
        self.Edit.setFont(QFont('Consolas', 20))
        verticalLayout.addWidget(self.label)
        verticalLayout.addWidget(self.Edit)
        horizontalLayout.addLayout(verticalLayout)
        verticalLayout_2 = QVBoxLayout()
        verticalLayout_2.addLayout(horizontalLayout)
        self.label.setStyleSheet("background-color: rgb(255, 255, 255,6 0);")
        self.table_widget.setStyleSheet("background-color: rgb(255, 255, 255, 60);")
        self.Browser.setStyleSheet("background-color: rgb(255, 255, 255, 60);")
        self.Edit.setStyleSheet("background-color: rgb(255, 255, 255, 60);")
        self.label.setStyleSheet("color:white")
        widget = QWidget()
        self.setCentralWidget(widget)  # 建立的widget在窗体的中间位置
        widget.setLayout(verticalLayout_2)

        # Window设置
        self.resize(1500, 900)
        self.center()
        self.setFont(QFont('华文楷体', 10))
        self.setWindowTitle('编译器')
        self.show()

    def center(self):
        # 得到主窗体的框架信息
        qr = self.frameGeometry()
        # 得到桌面的中心
        cp = QDesktopWidget().availableGeometry().center()
        # 框架的中心与桌面中心对齐
        qr.moveCenter(cp)
        # 自身窗体的左上角与框架的左上角对齐
        self.move(qr.topLeft())


    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self,
                                     '编译器',
                                     "是否要退出应用程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


    def Lex(self):
        code=self.Edit.toPlainText()
        with    open('yuan.txt', 'w') as f:
            f.write(code)
        codeview=Util.FileReadUtil.getcode('yuan.txt')
        self.Browser.setText(codeview)
        res=Util.LexerUtil.lexer()
        self.table_widget.setRowCount(len(res))
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['TAG','分类','符号'])
        for one in res:

            self.table_widget.setItem(one.getnumber()-1, 0, QTableWidgetItem(str(one.gettag())))
            self.table_widget.setItem(one.getnumber()-1, 1, QTableWidgetItem(one.getdetail()))
            self.table_widget.setItem(one.getnumber()-1, 2,QTableWidgetItem(one.getsymbol()))
    def parse(self):
        code = self.Edit.toPlainText()
        with    open('yuan.txt', 'w') as f:
            f.write(code)
        codeview = Util.FileReadUtil.getcode('yuan.txt')
        self.Browser.setText(codeview)
        p=Util.ParserUtil(Util.LexerUtil.lexer())
        p.parser()
        myres=p.res
        flag=p.flag
        self.table_widget.setRowCount(len(myres)+1)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(['过程'])
        if flag==True:
            self.table_widget.setItem(0,0,QTableWidgetItem('成功'))
        else:
            self.table_widget.setItem(0,0,QTableWidgetItem('分析失败'))
        self.table_widget.item(0,0).setForeground(QBrush(QColor(255,0,0)))
        for i in range(len(myres)):
            self.table_widget.setItem(i+1,0,QTableWidgetItem(myres[i]))
    def gettable(self):
        code = self.Edit.toPlainText()
        with    open('yuan.txt', 'w') as f:
            f.write(code)
        codeview = Util.FileReadUtil.getcode('yuan.txt')
        self.Browser.setText(codeview)
        ll_analyzer = Util.LLOneAnalyzer(start=Util.LLOneAnalyzer.start, overs=Util.LLOneAnalyzer.overs,
                                    productions=Util.LLOneAnalyzer.productions)

        '''
        if ll_analyzer.flag == False:
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            self.table_widget.setItem(0, 0, QTableWidgetItem('该文法不是LL1文法'))
            self.table_widget.item(0, 0).setForeground(QBrush(QColor(255, 0, 0)))
        else:
        '''
        ll_analyzer.get_analyse_table()
        self.table_widget.setRowCount(len(ll_analyzer.analyse_table))
        self.table_widget.setColumnCount(len(ll_analyzer.analyse_table['M'].keys()))
        self.table_widget.setVerticalHeaderLabels(list(ll_analyzer.analyse_table.keys()))
        self.table_widget.setHorizontalHeaderLabels(list(ll_analyzer.analyse_table['M'].keys()))
        i = 0
        j = 0
        for one in ll_analyzer.analyse_table:
            j = 0
            for oneone in ll_analyzer.analyse_table[one]:
                self.table_widget.setItem(i, j, QTableWidgetItem(str(ll_analyzer.analyse_table[one][oneone][0])))
                j = j + 1
            i = i + 1
        if ll_analyzer.flag==False:
            self.Browser.setText('不是LL文法')

    def getprocess(self):
        code = self.Edit.toPlainText()
        with    open('yuan.txt', 'w') as f:
            f.write(code)
        codeview = Util.FileReadUtil.getcode('yuan.txt')
        self.Browser.setText(codeview)
        ll_analyzer = Util.LLOneAnalyzer(start=Util.LLOneAnalyzer.start, overs=Util.LLOneAnalyzer.overs,
                                         productions=Util.LLOneAnalyzer.productions)
        if ll_analyzer.flag == False:
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            self.table_widget.setItem(0, 0, QTableWidgetItem('该文法不是LL1文法'))
            self.table_widget.item(0, 0).setForeground(QBrush(QColor(255, 0, 0)))
        else:
            ll_analyzer.get_analyse_table()
            res=ll_analyzer.analyse(Util.LexerUtil.lexer())
            self.table_widget.setRowCount(len(res[1]))
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(['分析栈','符号串','动作'])
            i = 0

            for one in range(1,4):
                j = 0
                for oneone in res[one]:
                    self.table_widget.setItem(j, one-1, QTableWidgetItem(str(oneone)))
                    j = j + 1

    def funleft(self):
        code = self.Edit.toPlainText()
        with    open('yuan.txt', 'w') as f:
            f.write(code)
        codeview = Util.FileReadUtil.getcode('yuan.txt')
        self.Browser.setText(codeview)
        ll_analyzer = Util.LLOneAnalyzer(start=Util.LLOneAnalyzer.start, overs=Util.LLOneAnalyzer.overs,
                                         productions=Util.LLOneAnalyzer.productions)
        view='原来产生式\n'
        for nonterminal in list(Util.LLOneAnalyzer.productions.keys()):
            for right in Util.LLOneAnalyzer.productions[nonterminal]:
                    view='%s\n%s-->%s'%(view,nonterminal,right)
        view = view.strip('\n')
        view=view+'\n消除左递归和左公共因子后为\n'
        for nonterminal in ll_analyzer.nontermainals:
            for right in ll_analyzer.productions[nonterminal]:
                    view = '%s\n%s-->%s' % (view, nonterminal, right)
        view = view.strip('\n')
        self.Browser.setText(view)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = CMainWindow()
    MainWindow.setObjectName("MainWindow")
    #todo 1 设置窗口背景图片
    MainWindow.setStyleSheet("#MainWindow{border-image:url(./1.jpg);}")
    sys.exit(app.exec_())