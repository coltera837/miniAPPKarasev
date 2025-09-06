from PySide6.QtWidgets import (QWidget, QApplication, QPushButton, QLineEdit,
                               QListView, QLabel, QVBoxLayout, QMessageBox,
                               QHBoxLayout, QSpinBox, QGroupBox)
from PySide6.QtGui import QStandardItemModel, QStandardItem
import requests
from requests.exceptions import RequestException
from datetime import date, datetime


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.current_skip = 0
        self.current_limit = 10
        self.total_records = 0
        self.total_pages = 1

        self.setWindowTitle("Телефонная книжка")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        label = QLabel("Номер телефона:")
        self.number = QLineEdit()
        self.number.setPlaceholderText("+79807060972")
        self.number.setMaxLength(12)

        but1 = QPushButton("Внести")

        pagination_layout = QHBoxLayout()

        pagination_layout.addWidget(QLabel("Страница:"))
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self.on_page_changed)
        pagination_layout.addWidget(self.page_spin)

        pagination_layout.addWidget(QLabel("Записей на страницу:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setMinimum(1)
        self.limit_spin.setMaximum(100)
        self.limit_spin.setValue(10)
        self.limit_spin.valueChanged.connect(self.on_limit_changed)
        pagination_layout.addWidget(self.limit_spin)

        but2 = QPushButton("Получить список")

        self.model = QStandardItemModel()

        response_list = QListView()
        response_list.setModel(self.model)

        self.status_label = QLabel("Готово")

        layout.addWidget(label)
        layout.addWidget(self.number)
        layout.addWidget(but1)
        layout.addWidget(but2)
        layout.addWidget(response_list)
        layout.addLayout(pagination_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        but1.clicked.connect(self.add_phone_number)
        but2.clicked.connect(self.get_response)

    def check_input_number(self):
        msg = QMessageBox()
        if len(self.number.text()) == 11 and self.number.text()[0] == '8':
            return True
        elif len(self.number.text()) == 12 and self.number.text()[0:2] == '+7':
            return True
        else:
            msg.critical(None, "Ошибка!",
                         "Введённый номер не соответствует формату номера телефона РФ",
                         QMessageBox.Ok)
            return False

    def add_phone_number(self):
        self.count += 1
        try:
            if self.check_input_number():
                data = {
                    'data': {
                        'number': self.number.text(),
                        'currentDate': str(date.today()),
                        'currentTime': datetime.now().strftime('%H:%M:%S'),
                        'clickOrder': self.count
                    }
                }
                print(f"Отправляемые данные: {data}")
                req = requests.post('http://127.0.0.1:8000/addPhoneNumber', json=data)
                print(f"Ответ сервера: {req.status_code}, {req.text}")
                req.raise_for_status()
                self.status_label.setText("Запись успешно добавлена")
        except RequestException as re:
            error_msg = f'Ошибка запроса: {re}'
            print(error_msg)
            self.status_label.setText(error_msg)
        except Exception as err:
            error_msg = f'Ошибка: {err}'
            print(error_msg)
            self.status_label.setText(error_msg)

    def get_response(self):
        try:
            params = {
                'skip': self.current_skip,
                'limit': self.current_limit
            }

            response = requests.get('http://127.0.0.1:8000/NumberList', params=params)
            print(f"GET ответ: статус {response.status_code}, текст: {response.text}")

            if response.status_code == 200:
                data = response.json()

                self.total_records = data['total']
                self.total_pages = data['total_pages']

                self.page_spin.blockSignals(True)
                self.page_spin.setMaximum(max(1, self.total_pages))
                self.page_spin.blockSignals(False)

                self.model.clear()
                self.model.setHorizontalHeaderLabels(["Телефон", "Дата", "Время", "Клик", "ID"])

                for item in data['records']:
                    number = item.get("number", "")
                    current_date = str(item.get("currentDate", ""))
                    current_time = str(item.get("currentTime", ""))
                    click_order = str(item.get("clickOrder", ""))
                    item_id = str(item.get("id", ""))

                    item_text = f"{number} | {current_date} | {current_time} | {click_order} | {item_id}"
                    self.model.appendRow(QStandardItem(item_text))

                self.status_label.setText(
                    f"Записей: {self.total_records} | "
                    f"Страница {data['current_page']} из {self.total_pages} | "
                    f"Показано: {len(data['records'])}"
                )

            response.raise_for_status()

        except RequestException as re:
            error_msg = f'Ошибка запроса: {re}'
            print(error_msg)
            self.status_label.setText(error_msg)
        except Exception as err:
            error_msg = f'Ошибка: {err}'
            print(error_msg)
            self.status_label.setText(error_msg)

    def on_page_changed(self, value):
        self.current_skip = (value - 1) * self.current_limit
        self.get_response()

    def on_limit_changed(self, value):
        self.current_limit = value
        self.current_skip = 0
        self.page_spin.setValue(1)
        self.get_response()


application = QApplication([])
ex = Window()
ex.show()
application.exec()