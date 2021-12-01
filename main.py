from main_ui import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QMainWindow, QApplication, QHeaderView
import sys
from PyQt5.QtCore import QThread
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import pandas as pd


class Get_Thread(QThread):
    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        keyword = window.lineEdit.text()

        chromedriver_autoinstaller.install(cwd=True)
        driver = webdriver.Chrome()
        outerbox = []
        for key in keyword.split(','):
            key = key.strip()
            driver.get('https://itemscout.io/')
            driver.implicitly_wait(10)
            time.sleep(random.random())
            search = driver.find_element(By.XPATH, '//input[@type="search"]')
            search.send_keys(key)
            search.send_keys(Keys.ENTER)
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".keyword-title-word")))
            rows = driver.find_elements(By.CLASS_NAME, 'search-page-summary-row')

            box = []
            for i in rows:
                box.append(i.text)
                break

            box2 = {}
            for i in box:
                infos = i.split('\n')
                box2['키워드'] = key
                for idx, val in enumerate(infos):
                    if idx != 0 and idx % 2 != 0:
                        if infos[0] + ' ' + infos[idx] not in box2:
                            box2[infos[0] + ' ' + infos[idx]] = infos[idx + 1]
                        else:
                            box2[infos[0] + ' ' + infos[idx]] += infos[idx + 1]

            table = driver.find_element(By.CLASS_NAME, 'market-trend-score.keyword_guide_market_trend_step8')
            for i in table.find_elements(By.CLASS_NAME, 'score-title')[:-1]:
                if i.text.split('\n')[1] not in box2:
                    box2[i.text.split('\n')[1]] = i.text.split('\n')[0]
                else:
                    box2[i.text.split('\n')[1]] += i.text.split('\n')[0]
            time.sleep(1)
            table = driver.find_element(By.CLASS_NAME, 'count-summary.keyword_guide_market_trend_step5')
            for i in table.find_elements(By.CLASS_NAME, 'count-view')[:-1]:
                if i.text.split('\n')[1] not in box2:
                    box2[i.text.split('\n')[0]] = i.text.split('\n')[1]
                else:
                    box2[i.text.split('\n')[0]] += i.text.split('\n')[1]

            outerbox.append(box2)
            time.sleep(3)
        driver.close()

        global df
        df = pd.DataFrame(outerbox)
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
        self.tableWidget.setColumnCount(9)
        global lists
        lists = ['키워드', 'Top 40 6개월 매출', 'Top 40 6개월 판매량', 'Top 40 평균 가격', '상품 종합 지표',
       '광고 종합 지표', '컨텐츠 종합 지표', '상품수', '한 달 검색수']
        self.tableWidget.setHorizontalHeaderLabels(lists)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pushButton_2.clicked.connect(self.export)

    def export(self):
        import re
        def str_to_int(x):
            if '억' in x:
                return int(str(re.sub(r'[^0-9]', '', x)) + '00000000')
            if '만원' in x:
                return int(str(re.sub(r'[^0-9]', '', x)) + '0000')
            else:
                return int(re.sub(r'[^0-9]', '', x))

        lists = list(df)
        for i in [1,2,3,7,8]:
            df[lists[i]] = df[lists[i]].apply(str_to_int)

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
