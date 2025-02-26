from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QColorDialog, QVBoxLayout, 
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QRubberBand
)
from PyQt6.QtGui import QColor, QPixmap, QImage
from PyQt6.QtCore import Qt, QRect
import numpy as np
import sys
import cv2

from PaintMixPredictor import PaintMixPredictor

class ColorPickerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Color Picker with Image")
        self.setGeometry(100, 100, 500, 500)

        self.colors = []  
        self.mixed_colors = []  # tuple of (rgb, amount)
        self.image = None  # Store uploaded image
        self.selected_area = None  # Store selected region

        layout = QVBoxLayout()

        # Button to pick a color manually
        self.button = QPushButton("Pick a color", self)
        self.button.clicked.connect(self.choose_color)
        layout.addWidget(self.button)

        # Button to upload an image
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_button)

        # Graphics View for image display
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        # Label to show selected color
        self.color_label = QLabel(" ", self)
        self.color_label.setStyleSheet("background-color: white; border: 1px solid black; min-height: 50px;")
        layout.addWidget(self.color_label)

        # RGB Value Label
        self.rgb_label = QLabel("RGB: ", self)
        layout.addWidget(self.rgb_label)

        # Done button for mixing colors
        self.done_button = QPushButton("Done", self)
        self.done_button.clicked.connect(self.finish_selection)
        layout.addWidget(self.done_button)

        self.setLayout(layout)

        # Rubber band for selection
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self.view)
        self.origin = None

        # Enable mouse tracking for selection
        self.view.viewport().installEventFilter(self)

    def choose_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            rgb_values = (color.red(), color.green(), color.blue())
            hex_value = color.name()

            # Show the selected color
            self.color_label.setStyleSheet(f"background-color: {hex_value}; border: 1px solid black;")
            self.rgb_label.setText(f"RGB: {rgb_values}")

            self.colors.append(rgb_values)  # Store RGB values

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)  # Load image using OpenCV
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)  # Convert to RGB format

            height, width, _ = self.image.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)

            self.scene.clear()
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)

    def eventFilter(self, source, event):
        """Handles mouse events for dragging a selection box."""
        if source == self.view.viewport():
            if event.type() == event.Type.MouseButtonPress:
                self.origin = event.pos()
                self.rubber_band.setGeometry(QRect(self.origin, self.origin))
                self.rubber_band.show()

            elif event.type() == event.Type.MouseMove:
                if self.origin:
                    rect = QRect(self.origin, event.pos()).normalized()
                    self.rubber_band.setGeometry(rect)

            elif event.type() == event.Type.MouseButtonRelease:
                if self.image is not None and self.origin:
                    self.rubber_band.hide()
                    rect = self.rubber_band.geometry()

                    # Convert to image coordinates
                    x1, y1 = self.view.mapToScene(rect.topLeft()).toPoint().x(), self.view.mapToScene(rect.topLeft()).toPoint().y()
                    x2, y2 = self.view.mapToScene(rect.bottomRight()).toPoint().x(), self.view.mapToScene(rect.bottomRight()).toPoint().y()

                    # Ensure valid cropping
                    x1, x2 = max(0, x1), min(self.image.shape[1], x2)
                    y1, y2 = max(0, y1), min(self.image.shape[0], y2)

                    if x2 > x1 and y2 > y1:
                        self.selected_area = self.image[y1:y2, x1:x2]
                        self.extract_color()

                self.origin = None  # Reset origin
        return super().eventFilter(source, event)

    def extract_color(self):
        """Extracts the average color from the selected region."""
        if self.selected_area is not None:
            avg_color = np.mean(self.selected_area, axis=(0, 1)).astype(int)
            avg_rgb = tuple(avg_color)

            hex_value = QColor(*avg_rgb).name()

            # Update the UI
            self.color_label.setStyleSheet(f"background-color: {hex_value}; border: 1px solid black;")
            self.rgb_label.setText(f"Selected RGB: {avg_rgb}")

            self.colors.append(avg_rgb)

    def finish_selection(self):
        """Handles color mixing from manual picks and image selections."""
        if not self.colors:
            print("No colors selected!")
            return

        for rgb in self.colors:
            amount, ok = QInputDialog.getInt(self, "Color Amount", f"Enter amount for color {rgb}:", min=1, max=100)
            if ok:
                self.mixed_colors.append((rgb, amount))

        print("Final color mix:", self.mixed_colors)
        mixed_color = self.mix()
        mixed_color_hex = QColor(*mixed_color).name()

        # Show mixed color
        self.mixed_color_label = QLabel(" ", self)
        self.mixed_color_label.setStyleSheet(f"background-color: {mixed_color_hex}; border: 1px solid black; min-height: 50px;")
        self.layout().addWidget(self.mixed_color_label)

        self.rgb_label.setText(f"Mixed RGB: {tuple(mixed_color)}")

    def mix(self):
        weighted_sum = 0
        for rgb, amt in self.mixed_colors:
            weighted_sum += np.array(rgb) * amt / 100

        rounded = np.round(weighted_sum).astype(int)

        return rounded