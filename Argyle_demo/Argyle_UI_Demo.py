import sys, time, webbrowser

from dateutil.relativedelta import relativedelta

from PySide6.QtCore import Qt, QDateTime, QSize

from PySide6.QtWidgets import QApplication,QMainWindow,QLabel,QWidget,QDateEdit,QHBoxLayout,QVBoxLayout,QProgressBar,QPushButton,QDial,QStatusBar,QToolBar

from PySide6.QtGui import QAction, QIcon

from RestCrawler import RestCrawler

 

class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)

 

        self.setWindowTitle('Argyle Interview Demo 1.0')

 

        # initialze sub layout

        main_layout=QVBoxLayout()

        layout_dial=QHBoxLayout()

        layout_start_date=QHBoxLayout()

        layout_end_date=QHBoxLayout()

        layout_pbtn=QVBoxLayout()

 
        # initialize toolbar
        self.toolbar=QToolBar('My Toolbox')
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)

        ## define icon 1 and ties to action 1
        icon_action=QAction(QIcon(r'/home/ranco/Python/Perigon_Demo/open_web.png'),'Open Website',self)
        icon_action.setStatusTip('Open up data source page')
        icon_action.triggered.connect(self.open_source_page)
        icon_action.setCheckable(True)
        self.toolbar.addAction(icon_action)

        # initialize label 1: Start date

        self.label1=QLabel('Months covered: 03')

        self.label2=QLabel('Start Date')

        self.label3=QLabel('End Date: ')

        self.label4=QLabel('')

       

        # initialize date edit for start date

        self.dateedit = QDateEdit(calendarPopup=True)
        self.dateedit.setStatusTip('Choose a start date')

        self.dateedit.setDisplayFormat("dd/MM/yyyy")

        self.dateedit.setDateTime(QDateTime.currentDateTime().addYears(-5))

        # print(type(self.dateedit.date().toPyDate()))

 

        # initialize dial

        self.dial=QDial()
        self.dial.setStatusTip('Rotate to select end date')

        self.dial.setRange(0,99)

        self.dial.setValue(3)

        self.dial.setNotchesVisible(True)

        self.dial.setNotchTarget(5)

        self.dial.sliderMoved.connect(self.slider_position)

 

        # initialize progress bar

        self.pbar=QProgressBar()

        self.pbar.setToolTip('Progress bar for downloadables')

        self.pbar.setStatusTip('Progress bar for downloadables')

        self.pbar.setRange(0,100)

 

        # initialize push button

        self.btn=QPushButton('Run')

        self.btn.setStatusTip('Run main program')

        self.btn.clicked.connect(self.run_main)

 

        # initialize status bar

        self.sbar=QStatusBar()

        self.sbar.showMessage("Ready")

        self.sbar.setStyleSheet('background-color: rgb(132,169,140)')

        self.setStatusBar(self.sbar)

 

        # set individual layout

        layout_dial.addWidget(self.label1,alignment=Qt.AlignmentFlag.AlignLeft)

        layout_dial.addWidget(self.dial)

        layout_dial.setContentsMargins(0,0,0,0)

        layout_dial.setSpacing(60)

 

        layout_start_date.addWidget(self.label2,alignment=Qt.AlignmentFlag.AlignLeft)

        layout_start_date.addWidget(self.dateedit)

 

        layout_end_date.addWidget(self.label3)

        layout_end_date.addWidget(self.label4)

        layout_end_date.setSpacing(19)

       

        layout_pbtn.addWidget(self.pbar)

        layout_pbtn.addWidget(self.btn)

        layout_pbtn.setContentsMargins(0,60,0,0)

        layout_pbtn.setSpacing(10)

 

        # add layouts

        main_layout.addLayout(layout_dial)

        main_layout.addLayout(layout_start_date)

        main_layout.addLayout(layout_end_date)

        main_layout.addLayout(layout_pbtn)

 

        widget=QWidget()

        widget.setLayout(main_layout)

        self.setCentralWidget(widget)

   

    def slider_position(self,pos):

        self.label1.setText(f"Months covered: {pos:02}")

 

        # convert to python datetime object and calculate end date

        start_date=self.dateedit.date().toPython()

        end_date=self.end_date_calc(start_date,pos)

        self.label4.setText(f"{end_date}")

 

        # update progress bar maximum

        self.pbar.setRange(0,pos)

 

    def end_date_calc(self, start_date_obj, delta):

        return (start_date_obj+relativedelta(months=+(delta-1), day=31)).strftime(r'%d/%m/%Y')

 

    def run_main(self,start_date):
        print(self.dial.value())
        if self.dial.value()==0:
            self.sbar.showMessage('Cannot analyse one 1 month. Plz move dial.')
            return None

        # run Rest rawler

        options = ['Core Strategy', 'Balanced', 'Capital Stable', 'Diversified', 'High Growth', 'Cash', 'Bonds', 'Shares','Property','Australian Shares', 'Australian Shares - Indexed', 'Overseas Shares', 'Overseas Shares - Indexed']

 

        MyCrawler = RestCrawler(

                                self,

 

                                folder_name='Raw_Rest_data',

 

                                start_date = self.dateedit.date().toPython().strftime(r'%d/%m/%Y'),

 

                                months_under_analysis=self.dial.value(),

 

                                funds=options,

 

                                debug=False)

 

        # run the web crawler

       

        # self.open_browser()

 

        MyCrawler.run()

       

 

    def open_browser(self):

        webbrowser.open('http://127.0.0.1:8000')


    def open_source_page(self):
        webbrowser.open_new_tab('https://rest.com.au/member/investments/performance')


 

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    # window.resize(300,250)

    window.show()

    app.exec()