import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QStackedWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QGridLayout, QProgressBar
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt6.QtGui import QDesktopServices
import os
import pandas as pd

class OfferScraperThread(QThread):
    finished = pyqtSignal()

    def run(self):
        exec(open('offertag.py').read())
        self.finished.emit()

class OfferGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # exec(open('offertag.py').read())
        self.setWindowTitle("Offers")
        self.setWindowIcon(QIcon(os.path.join('assets','icon.png')))
        self.setGeometry(300, 100, 880, 600)
        self.QWidget = QWidget()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Add refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_offers)
        layout.addWidget(refresh_button)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        
        container_layout = QGridLayout(container)
        container_layout.setHorizontalSpacing(10)
        container_layout.setVerticalSpacing(10)

        self.container_layout = container_layout  # Save reference to layout
        self.load_offers(container_layout)

        scroll.setWidget(container)
        layout.addWidget(scroll)
        self.QWidget.setLayout(layout)
        self.setCentralWidget(self.QWidget)

    def load_offers(self, layout):
        print("Loading offers...")
        df = pd.read_csv('offers.csv')
        row_position = 0
        col_position = 0
        for index, row in df.iterrows():
            offer_frame = QFrame()
            offer_layout = QVBoxLayout()

            # Create a label for the image
            image_label = QLabel()
            title = row['title']
            pixmap = QPixmap(os.path.join('assets', f'{title}.png'))  # Assuming a default image
            image_label.setPixmap(pixmap)
            image_label.setScaledContents(True)
            image_label.setFixedHeight(100)  # Adjusted height to fit more items vertically

            # Create a container for price and discount
            price_discount_container = QWidget()
            price_discount_layout = QHBoxLayout(price_discount_container)
            price_discount_layout.setContentsMargins(0, 0, 0, 0)
            price_discount_layout.setSpacing(0)

            price_label = QLabel(f"Price: {row['price']}")
            discount_label = QLabel(f"Discount: {row.get('discount', 'N/A')}")  # Assuming discount column exists

            price_discount_layout.addWidget(price_label)
            price_discount_layout.addWidget(discount_label)
            price_discount_container.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); color: white;")
            price_discount_container.setFixedHeight(30)

            # Create a container for the image and price/discount
            image_container = QVBoxLayout()
            image_container.addWidget(image_label)
            image_container.addWidget(price_discount_container)

            title_label = QLabel(f"Title: {row['title']}")

            offer_layout.addLayout(image_container)
            offer_layout.addWidget(title_label)
            offer_frame.setLayout(offer_layout)
            offer_frame.setFrameShape(QFrame.Shape.Box)
            offer_frame.setFixedHeight(200)  # Adjusted height to make the container smaller

            # Add click event to open the link
            offer_frame.mousePressEvent = lambda event, url=row['link']: self.open_link(event, url)

            layout.addWidget(offer_frame, row_position, col_position, 1, 1)  # Adjusted to use row and column span

            col_position += 1
            if col_position >= 2:  # Adjusted to fit 2 items per row
                col_position = 0
                row_position += 1

        print("Loading Complete!")

    def refresh_offers(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Set to indeterminate mode
        self.scraper_thread = OfferScraperThread()
        self.scraper_thread.finished.connect(self.on_scraper_finished)
        self.scraper_thread.start()

    def on_scraper_finished(self):
        # Clear existing offers
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Reload offers
        self.load_offers(self.container_layout)
        self.progress_bar.setVisible(False)
        print("========================Offers refreshed!========================")

    def open_link(self, event, url):
        if event.button() == Qt.MouseButton.LeftButton:
            QDesktopServices.openUrl(QUrl(url))

app = QApplication(sys.argv)
window = OfferGUI()
window.show()
sys.exit(app.exec())