import csv
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit
from multiprocessing import Pool


def process_image(image):
    data_ = []
    gray = cv2.cvtColor(image[0], cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)[1]

    # Поиск контуров на изображении
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    stars = []
    planets = []
    galactics = []
    for contour in contours:
        object = None
        if cv2.contourArea(contour) > 500:
            object = "Galactic"
            galactics.append(contour)
        elif cv2.contourArea(contour) > 50:
            object = "Planet"
            planets.append(contour)
        else:
            object = "Star"
            stars.append(contour)
        x, y, contourWidth, contourHeight = cv2.boundingRect(contour)

        data_.append([f"result/image{image[1] + 1}.png", str(image[1] + 1), f"{(x, y)}", object, f"{contourWidth * contourHeight}"])
    cv2.drawContours(image[0], galactics, -1, (0, 255, 0), 2)
    cv2.drawContours(image[0], planets, -1, (255, 0, 0), 2)
    cv2.drawContours(image[0], stars, -1, (0, 0, 255), 2)
    cv2.imwrite(f"result/image{image[1] + 1}.png", image[0])
    return {
        'file': f"result/image{image[1] + 1}.png",
        'galactics_count': len(galactics),
        'planets_count': len(planets),
        'stars_count': len(stars),
        'data': data_
    }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.result_file = None
        self.setWindowTitle("Анализ космических данных")
        self.setGeometry(100, 100, 600, 400)

        self.button = QPushButton("Выбрать изображения", self)
        self.button.clicked.connect(self.load_images)
        self.button.resize(200, 40)
        self.button.move(70, 50)

        self.button2 = QPushButton("Выбрать файл", self)
        self.button2.clicked.connect(self.load_file)
        self.button2.resize(200, 40)
        self.button2.move(330, 50)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(50, 100, 500, 250)

    def load_file(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "",
                                              options=options)
        self.result_file = file

    def load_images(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Image Files (*.png *.jpg *.jpeg)",
                                              options=options)

        if file:
            self.analyze_images(file)

    def analyze_images(self, image_path):
        image_lists = []
        file = cv2.imread(image_path)
        n = 10
        a = file.shape[0]
        for i in range(n):
            if i == n - 1:
                k = a
            else:
                k = (i + 1) * (a // n + 1)
            image = file[i * (a // n + 1):k, :]
            image_lists.append([image, i])
        with Pool() as pool:
            results = pool.map(process_image, image_lists)

        self.display_results(results)

    def display_results(self, results):
        output = ""
        galactics_count = 0
        planets_count = 0
        stars_count = 0
        final_data = []
        for result in results:
            output += (f"Изображение: {result['file']}, Количество галактик: {result['galactics_count']},\n"
                       f"Количество планет: {result['planets_count']}, Количество звезд: {result['stars_count']}\n")
            galactics_count += result['galactics_count']
            planets_count += result['planets_count']
            stars_count += result['stars_count']
            final_data.extend(result["data"])
        output += f"\nВсего галактик: {galactics_count}\nВсего планет: {planets_count}\nВсего звезд: {stars_count}"
        self.text_edit.setPlainText(output)
        file_output = open(self.result_file, mode="w", encoding="utf8")
        file_writer = csv.writer(file_output, delimiter=";")
        for i in final_data:
            file_writer.writerow(i)
        file_output.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
