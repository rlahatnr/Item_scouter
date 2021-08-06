from main_ui import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QMainWindow, QTableWidget, QApplication,QHeaderView
import sys
from PyQt5.QtCore import QThread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Get_Thread(QThread):
    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        keyword = window.lineEdit.text()

        driver = webdriver.Chrome()
        outerbox=[]
        for key in keyword.replace(' ','').split(','):
            driver.get('https://itemscout.io/')
            driver.implicitly_wait(10)
            time.sleep(random.random())
            search = driver.find_element_by_class_name('wow.fadeInUp')
            search.send_keys(key)
            search.send_keys(Keys.ENTER)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".keyword-title-word")))
            row = driver.find_elements_by_class_name('search-page-summary-row')[0]

            import pandas as pd
            innerbox=[]
            for idx, val in enumerate(row.find_elements_by_class_name('count-stat')):
                innerbox.append(val.text)
            innerbox.insert(0, key)
            innerbox.insert(4, driver.find_element_by_class_name('count-summary').find_elements_by_class_name('count-stat')[0].text)
            innerbox.insert(5, driver.find_element_by_class_name('count-summary').find_elements_by_class_name('count-stat')[1].text)
            innerbox.insert(6, driver.find_elements_by_class_name('stat-score.larger')[0].text.split('\n')[0])
            innerbox.insert(7, driver.find_elements_by_class_name('stat-score.larger')[0].text.split('\n')[1])
            outerbox.append(innerbox)
            global df
            df = pd.DataFrame(outerbox, columns=lists)
            window.tableWidget.setRowCount(df.shape[0])
            window.tableWidget.setColumnCount(df.shape[1])

            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    window.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.go_search)
        self.tableWidget.setColumnCount(8)
        global lists
        lists = '키워드, 6개월 매출, 6개월 판매량, 평균가격, 상품수, 한달 검색수, 경쟁강도, 경쟁강도 지표'.replace(' ','').split(',')
        self.tableWidget.setHorizontalHeaderLabels(lists)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pushButton_2.clicked.connect(self.export)

    def export(self):
        import re
        def str_to_int(x):
            if '억' in x:
                return int(str(re.sub(r'[^0-9]', '', x))+'00000000')
            if '만원' in x:
                return int(str(re.sub(r'[^0-9]', '', x))+'0000')
            else:
                return int(re.sub(r'[^0-9]', '', x))

        lists = list(df)
        df[lists[1]] = df[lists[1]].apply(str_to_int)
        df[lists[2]] = df[lists[2]].apply(str_to_int)
        df[lists[3]] = df[lists[3]].apply(str_to_int)
        df[lists[4]] = df[lists[4]].apply(str_to_int)
        df[lists[5]] = df[lists[5]].apply(str_to_int)
        df[lists[6]] = df[lists[6]].astype(float)

        df.to_excel('result.xlsx', index=False)
        msg = QMessageBox()
        msg.setWindowTitle("File saved.")
        msg.setText('result.xlsx 저장 완료.\n프로그램이 있는 폴더에서 확인하실 수 있습니다.')

        x = msg.exec()
    def go_search(self):
        thread = Get_Thread(self)
        thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
