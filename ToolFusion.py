"""
Multi-Tool Utility Suite – Professional Edition with Progress Indicators
-------------------------------------------------------------------------

This application bundles several useful tools into a single, attractive GUI,
complete with progress bars to show task progress and detailed on-screen
user manuals.

Tools:
1. Image Resizer/Converter
   - Resize images and convert them between popular formats.
   - **User Manual:** Select images, adjust dimensions/format, choose an output folder,
     and click “Convert/Resize Images”. The progress bar shows conversion progress.

2. PDF Merger/Splitter
   - Merge multiple PDFs or split a PDF into individual pages or a range.
   - **User Manual:** For merging, add PDFs then click “Merge PDFs” (progress shown).
     For splitting, select a PDF, choose split options, then click “Split PDF” (progress shown).

3. Screenshot & OCR
   - Capture a full-screen screenshot and extract text using EasyOCR.
   - **User Manual:** Click “Take Screenshot” then “Perform OCR”. A progress bar indicates task completion.

4. To-Do List Manager
   - Manage tasks: add, remove, mark as complete, and save/load your list.
   - **User Manual:** Enter tasks and click “Add Task”. Use the provided buttons to manage your list.

5. Password Generator
   - Generate a secure random password based on selected criteria.
   - **User Manual:** Adjust password settings and click “Generate Password”. Use “Copy to Clipboard” as needed.

Required Packages:
    PyQt5, Pillow, PyPDF2, pyautogui, easyocr

Install them via:
    pip install PyQt5 Pillow PyPDF2 pyautogui easyocr

Usage:
    python app.py
"""

import sys
import os
import random
import string

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QFileDialog, QComboBox, QSpinBox,
    QCheckBox, QTabWidget, QProgressBar
)
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer

# Pillow for image processing
from PIL import Image

# PyPDF2 for PDF operations
import PyPDF2

# pyautogui for screenshots
import pyautogui

# easyocr for OCR functionality
import easyocr

# -------------------- Custom Style Sheet -------------------- #
STYLE_SHEET = """
/* General Widget Style */
QWidget {
    background-color: #f5f5f5;
    font-family: 'Segoe UI';
    font-size: 10pt;
}

/* Push Button Style */
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #45a049;
}

/* Input fields */
QLineEdit, QSpinBox, QComboBox, QTextEdit, QListWidget {
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px;
}

/* Tab Widget Pane */
QTabWidget::pane {
    border: 1px solid #ccc;
    background: white;
}

/* Tab Bar Styles */
QTabBar::tab {
    background: #e0e0e0;
    padding: 8px;
    margin: 2px;
    border-radius: 4px;
}
QTabBar::tab:selected {
    background: #ffffff;
    border: 1px solid #ccc;
}

/* Instruction Label Style */
QLabel#instructionLabel {
    font-style: italic;
    color: #555;
    background-color: #e8e8e8;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 6px;
}
"""

# -------------------- Image Resizer/Converter Tab -------------------- #
class ImageConverterTab(QWidget):
    """
    Allows users to select images, resize them, and convert them to a desired format.
    Displays a progress bar to indicate processing progress.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Header and instructions
        header = QLabel("Image Resizer/Converter")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel(
            "User Manual: Select images, adjust width/height (maintain aspect ratio if needed), choose the output format and folder, then click 'Convert/Resize Images'."
        )
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Select images button
        self.selectImagesBtn = QPushButton("Select Images")
        self.selectImagesBtn.setToolTip("Click to select one or more image files.")
        self.selectImagesBtn.clicked.connect(self.selectImages)
        layout.addWidget(self.selectImagesBtn)
        
        # List of selected images
        self.imageList = QListWidget()
        layout.addWidget(self.imageList)
        
        # Format selection
        formatLayout = QHBoxLayout()
        formatLabel = QLabel("Target Format:")
        self.formatCombo = QComboBox()
        self.formatCombo.addItems(["JPEG", "PNG", "BMP", "GIF"])
        formatLayout.addWidget(formatLabel)
        formatLayout.addWidget(self.formatCombo)
        layout.addLayout(formatLayout)
        
        # Resize options
        resizeLayout = QHBoxLayout()
        widthLabel = QLabel("Width:")
        self.widthSpin = QSpinBox()
        self.widthSpin.setRange(1, 10000)
        self.widthSpin.setValue(800)
        heightLabel = QLabel("Height:")
        self.heightSpin = QSpinBox()
        self.heightSpin.setRange(1, 10000)
        self.heightSpin.setValue(600)
        self.aspectCheckbox = QCheckBox("Maintain Aspect Ratio")
        self.aspectCheckbox.setChecked(True)
        resizeLayout.addWidget(widthLabel)
        resizeLayout.addWidget(self.widthSpin)
        resizeLayout.addWidget(heightLabel)
        resizeLayout.addWidget(self.heightSpin)
        resizeLayout.addWidget(self.aspectCheckbox)
        layout.addLayout(resizeLayout)
        
        # Output folder selection
        outputLayout = QHBoxLayout()
        self.outputPathEdit = QLineEdit()
        self.outputPathEdit.setPlaceholderText("Select Output Folder")
        self.selectOutputBtn = QPushButton("Browse")
        self.selectOutputBtn.clicked.connect(self.selectOutputFolder)
        outputLayout.addWidget(self.outputPathEdit)
        outputLayout.addWidget(self.selectOutputBtn)
        layout.addLayout(outputLayout)
        
        # Process button and progress bar
        self.processBtn = QPushButton("Convert/Resize Images")
        self.processBtn.clicked.connect(self.processImages)
        layout.addWidget(self.processBtn)
        
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)
        
        # Log area
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)
        
        self.setLayout(layout)
    
    def selectImages(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if files:
            self.imageList.clear()
            for file in files:
                self.imageList.addItem(file)
    
    def selectOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.outputPathEdit.setText(folder)
    
    def processImages(self):
        total = self.imageList.count()
        if total == 0:
            self.logText.append("Error: No images selected.")
            return
        
        target_format = self.formatCombo.currentText().lower()
        target_width = self.widthSpin.value()
        target_height = self.heightSpin.value()
        maintain_aspect = self.aspectCheckbox.isChecked()
        output_folder = self.outputPathEdit.text()
        
        if not output_folder:
            self.logText.append("Error: Please select an output folder.")
            return
        
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(0)
        
        for i in range(total):
            file_path = self.imageList.item(i).text()
            try:
                img = Image.open(file_path)
                original_size = img.size
                if maintain_aspect:
                    img.thumbnail((target_width, target_height))
                else:
                    img = img.resize((target_width, target_height))
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(output_folder, f"{base_name}.{target_format}")
                if target_format == "jpeg":
                    img = img.convert("RGB")
                    img.save(output_file, quality=85)
                else:
                    img.save(output_file)
                self.logText.append(f"Processed: {file_path} -> {output_file} (from {original_size} to {img.size})")
            except Exception as e:
                self.logText.append(f"Error processing {file_path}: {str(e)}")
            # Update progress bar
            self.progressBar.setValue(i+1)
            QApplication.processEvents()  # Allow UI to update

# -------------------- PDF Merger/Splitter Tab -------------------- #
class PDFMergerSplitterTab(QWidget):
    """
    Provides PDF merging and splitting capabilities with progress feedback.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selectedPDFFile = ""
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        header = QLabel("PDF Merger/Splitter")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel(
            "User Manual: To merge PDFs, add your PDF files and click 'Merge PDFs'.\n"
            "For splitting, select a PDF, choose split options, then click 'Split PDF'."
        )
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Merge Section
        mergeLabel = QLabel("Merge PDFs")
        mergeLabel.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(mergeLabel)
        
        mergeLayout = QHBoxLayout()
        self.addPDFBtn = QPushButton("Add PDFs")
        self.addPDFBtn.clicked.connect(self.addPDFFiles)
        self.mergePDFBtn = QPushButton("Merge PDFs")
        self.mergePDFBtn.clicked.connect(self.mergePDFs)
        mergeLayout.addWidget(self.addPDFBtn)
        mergeLayout.addWidget(self.mergePDFBtn)
        layout.addLayout(mergeLayout)
        
        self.pdfList = QListWidget()
        layout.addWidget(self.pdfList)
        
        self.mergeProgressBar = QProgressBar()
        self.mergeProgressBar.setValue(0)
        layout.addWidget(self.mergeProgressBar)
        
        # Split Section
        splitLabel = QLabel("Split PDF")
        splitLabel.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(splitLabel)
        
        splitLayout = QHBoxLayout()
        self.selectPDFBtn = QPushButton("Select PDF")
        self.selectPDFBtn.clicked.connect(self.selectPDFFile)
        splitLayout.addWidget(self.selectPDFBtn)
        self.splitAllCheckbox = QCheckBox("Split All Pages")
        self.splitAllCheckbox.setChecked(True)
        splitLayout.addWidget(self.splitAllCheckbox)
        self.startPageSpin = QSpinBox()
        self.startPageSpin.setRange(1, 1000)
        self.startPageSpin.setValue(1)
        splitLayout.addWidget(QLabel("Start Page:"))
        splitLayout.addWidget(self.startPageSpin)
        self.endPageSpin = QSpinBox()
        self.endPageSpin.setRange(1, 1000)
        self.endPageSpin.setValue(1)
        splitLayout.addWidget(QLabel("End Page:"))
        splitLayout.addWidget(self.endPageSpin)
        self.splitPDFBtn = QPushButton("Split PDF")
        self.splitPDFBtn.clicked.connect(self.splitPDF)
        splitLayout.addWidget(self.splitPDFBtn)
        layout.addLayout(splitLayout)
        
        outputLayout = QHBoxLayout()
        self.splitOutputEdit = QLineEdit()
        self.splitOutputEdit.setPlaceholderText("Select Output Folder")
        self.selectSplitOutputBtn = QPushButton("Browse")
        self.selectSplitOutputBtn.clicked.connect(self.selectSplitOutputFolder)
        outputLayout.addWidget(self.splitOutputEdit)
        outputLayout.addWidget(self.selectSplitOutputBtn)
        layout.addLayout(outputLayout)
        
        self.splitProgressBar = QProgressBar()
        self.splitProgressBar.setValue(0)
        layout.addWidget(self.splitProgressBar)
        
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)
        
        self.setLayout(layout)
    
    def addPDFFiles(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            for file in files:
                self.pdfList.addItem(file)
    
    def mergePDFs(self):
        total = self.pdfList.count()
        if total == 0:
            self.logText.append("Error: No PDF files added for merging.")
            return
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if not output_file:
            return
        
        self.mergeProgressBar.setMaximum(total)
        self.mergeProgressBar.setValue(0)
        merger = PyPDF2.PdfFileMerger()
        try:
            for i in range(total):
                file_path = self.pdfList.item(i).text()
                merger.append(file_path)
                self.mergeProgressBar.setValue(i+1)
                QApplication.processEvents()
            merger.write(output_file)
            merger.close()
            self.logText.append(f"Merged PDFs saved to {output_file}")
        except Exception as e:
            self.logText.append(f"Error merging PDFs: {str(e)}")
    
    def selectPDFFile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.selectedPDFFile = file_path
            self.logText.append(f"Selected PDF for splitting: {file_path}")
            try:
                reader = PyPDF2.PdfFileReader(file_path)
                num_pages = reader.getNumPages()
                self.endPageSpin.setMaximum(num_pages)
                self.endPageSpin.setValue(num_pages)
            except Exception as e:
                self.logText.append(f"Error reading PDF: {str(e)}")
    
    def selectSplitOutputFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.splitOutputEdit.setText(folder)
    
    def splitPDF(self):
        if not self.selectedPDFFile:
            self.logText.append("Error: No PDF file selected for splitting.")
            return
        output_folder = self.splitOutputEdit.text()
        if not output_folder:
            self.logText.append("Error: Please select an output folder for split PDFs.")
            return
        
        try:
            reader = PyPDF2.PdfFileReader(self.selectedPDFFile)
            num_pages = reader.getNumPages()
            if self.splitAllCheckbox.isChecked():
                self.splitProgressBar.setMaximum(num_pages)
                self.splitProgressBar.setValue(0)
                for i in range(num_pages):
                    writer = PyPDF2.PdfFileWriter()
                    writer.addPage(reader.getPage(i))
                    output_file = os.path.join(output_folder, f"page_{i+1}.pdf")
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    self.splitProgressBar.setValue(i+1)
                    QApplication.processEvents()
                self.logText.append(f"Split all {num_pages} pages into individual PDFs.")
            else:
                start = self.startPageSpin.value() - 1
                end = self.endPageSpin.value()
                total_pages = end - start
                self.splitProgressBar.setMaximum(total_pages)
                self.splitProgressBar.setValue(0)
                writer = PyPDF2.PdfFileWriter()
                for i in range(start, end):
                    writer.addPage(reader.getPage(i))
                    self.splitProgressBar.setValue(i - start + 1)
                    QApplication.processEvents()
                output_file, _ = QFileDialog.getSaveFileName(self, "Save Split PDF", output_folder, "PDF Files (*.pdf)")
                if output_file:
                    with open(output_file, "wb") as f:
                        writer.write(f)
                    self.logText.append(f"Split PDF pages {start+1} to {end} saved to {output_file}")
        except Exception as e:
            self.logText.append(f"Error splitting PDF: {str(e)}")

# -------------------- Screenshot & OCR Tab -------------------- #
class ScreenshotOCRTab(QWidget):
    """
    Takes a full-screen screenshot and extracts text via OCR using EasyOCR.
    A progress bar indicates when the task is complete.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screenshot_path = None
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        header = QLabel("Screenshot & OCR")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel(
            "User Manual: Click 'Take Screenshot' to capture your screen, then click 'Perform OCR' to extract text."
        )
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        self.screenshotBtn = QPushButton("Take Screenshot")
        self.screenshotBtn.clicked.connect(self.takeScreenshot)
        layout.addWidget(self.screenshotBtn)
        
        self.imageLabel = QLabel("Screenshot Preview")
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setFixedHeight(200)
        layout.addWidget(self.imageLabel)
        
        self.ocrBtn = QPushButton("Perform OCR")
        self.ocrBtn.clicked.connect(self.performOCR)
        layout.addWidget(self.ocrBtn)
        
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)
        
        self.ocrResult = QTextEdit()
        self.ocrResult.setReadOnly(True)
        layout.addWidget(self.ocrResult)
        
        self.setLayout(layout)
    
    def takeScreenshot(self):
        try:
            self.screenshot_path = "screenshot.png"
            image = pyautogui.screenshot()
            image.save(self.screenshot_path)
            pixmap = QPixmap(self.screenshot_path)
            scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
            self.imageLabel.setPixmap(scaled_pixmap)
            self.ocrResult.append("Screenshot taken and saved.")
            self.progressBar.setValue(50)  # Partial progress
        except Exception as e:
            self.ocrResult.append(f"Error taking screenshot: {str(e)}")
    
    def performOCR(self):
        if not self.screenshot_path or not os.path.exists(self.screenshot_path):
            self.ocrResult.append("Error: No screenshot available. Please take a screenshot first.")
            return
        try:
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(self.screenshot_path)
            text = "\n".join([res[1] for res in results])
            self.ocrResult.append("OCR Result:\n" + text)
            self.progressBar.setValue(100)
        except Exception as e:
            self.ocrResult.append(f"Error performing OCR: {str(e)}")
            self.progressBar.setValue(0)

# -------------------- To-Do List Manager Tab -------------------- #
class ToDoListTab(QWidget):
    """
    Manages tasks with the ability to add, remove, mark complete, and save/load the list.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_file = "tasks.txt"
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        header = QLabel("To-Do List Manager")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel(
            "User Manual: Enter a task and click 'Add Task'. Select tasks to remove or mark as complete.\n"
            "Use 'Save Tasks' and 'Load Tasks' to manage your list."
        )
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        inputLayout = QHBoxLayout()
        self.taskInput = QLineEdit()
        self.taskInput.setPlaceholderText("Enter a new task")
        self.addTaskBtn = QPushButton("Add Task")
        self.addTaskBtn.clicked.connect(self.addTask)
        inputLayout.addWidget(self.taskInput)
        inputLayout.addWidget(self.addTaskBtn)
        layout.addLayout(inputLayout)
        
        self.taskList = QListWidget()
        layout.addWidget(self.taskList)
        
        btnLayout = QHBoxLayout()
        self.removeTaskBtn = QPushButton("Remove Selected Task")
        self.removeTaskBtn.clicked.connect(self.removeTask)
        self.markCompleteBtn = QPushButton("Mark as Complete")
        self.markCompleteBtn.clicked.connect(self.markComplete)
        btnLayout.addWidget(self.removeTaskBtn)
        btnLayout.addWidget(self.markCompleteBtn)
        layout.addLayout(btnLayout)
        
        fileLayout = QHBoxLayout()
        self.saveBtn = QPushButton("Save Tasks")
        self.saveBtn.clicked.connect(self.saveTasks)
        self.loadBtn = QPushButton("Load Tasks")
        self.loadBtn.clicked.connect(self.loadTasks)
        fileLayout.addWidget(self.saveBtn)
        fileLayout.addWidget(self.loadBtn)
        layout.addLayout(fileLayout)
        
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(self.logText)
        
        self.setLayout(layout)
    
    def addTask(self):
        task = self.taskInput.text().strip()
        if task:
            self.taskList.addItem(task)
            self.logText.append(f"Added task: {task}")
            self.taskInput.clear()
    
    def removeTask(self):
        selected_items = self.taskList.selectedItems()
        if not selected_items:
            self.logText.append("Error: No task selected.")
            return
        for item in selected_items:
            self.taskList.takeItem(self.taskList.row(item))
            self.logText.append(f"Removed task: {item.text()}")
    
    def markComplete(self):
        selected_items = self.taskList.selectedItems()
        if not selected_items:
            self.logText.append("Error: No task selected.")
            return
        for item in selected_items:
            item.setForeground(Qt.gray)
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
            self.logText.append(f"Marked as complete: {item.text()}")
    
    def saveTasks(self):
        try:
            with open(self.task_file, "w") as f:
                for index in range(self.taskList.count()):
                    f.write(self.taskList.item(index).text() + "\n")
            self.logText.append("Tasks saved successfully.")
        except Exception as e:
            self.logText.append(f"Error saving tasks: {str(e)}")
    
    def loadTasks(self):
        if not os.path.exists(self.task_file):
            self.logText.append("Error: No saved tasks found.")
            return
        try:
            self.taskList.clear()
            with open(self.task_file, "r") as f:
                tasks = f.readlines()
                for task in tasks:
                    self.taskList.addItem(task.strip())
            self.logText.append("Tasks loaded successfully.")
        except Exception as e:
            self.logText.append(f"Error loading tasks: {str(e)}")

# -------------------- Password Generator Tab -------------------- #
class PasswordGeneratorTab(QWidget):
    """
    Generates a secure random password based on user-selected criteria.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        header = QLabel("Password Generator")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        instructions = QLabel(
            "User Manual: Adjust the password length and choose which characters to include.\n"
            "Click 'Generate Password' to create a password, then click 'Copy to Clipboard' to copy it."
        )
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        lengthLayout = QHBoxLayout()
        lengthLabel = QLabel("Password Length:")
        self.lengthSpin = QSpinBox()
        self.lengthSpin.setRange(4, 64)
        self.lengthSpin.setValue(12)
        lengthLayout.addWidget(lengthLabel)
        lengthLayout.addWidget(self.lengthSpin)
        layout.addLayout(lengthLayout)
        
        self.uppercaseCheck = QCheckBox("Include Uppercase Letters")
        self.uppercaseCheck.setChecked(True)
        self.lowercaseCheck = QCheckBox("Include Lowercase Letters")
        self.lowercaseCheck.setChecked(True)
        self.numbersCheck = QCheckBox("Include Numbers")
        self.numbersCheck.setChecked(True)
        self.symbolsCheck = QCheckBox("Include Symbols")
        self.symbolsCheck.setChecked(True)
        layout.addWidget(self.uppercaseCheck)
        layout.addWidget(self.lowercaseCheck)
        layout.addWidget(self.numbersCheck)
        layout.addWidget(self.symbolsCheck)
        
        self.generateBtn = QPushButton("Generate Password")
        self.generateBtn.clicked.connect(self.generatePassword)
        layout.addWidget(self.generateBtn)
        
        self.passwordResult = QLineEdit()
        self.passwordResult.setReadOnly(True)
        layout.addWidget(self.passwordResult)
        
        self.copyBtn = QPushButton("Copy to Clipboard")
        self.copyBtn.clicked.connect(self.copyToClipboard)
        layout.addWidget(self.copyBtn)
        
        self.setLayout(layout)
    
    def generatePassword(self):
        length = self.lengthSpin.value()
        char_pool = ""
        if self.uppercaseCheck.isChecked():
            char_pool += string.ascii_uppercase
        if self.lowercaseCheck.isChecked():
            char_pool += string.ascii_lowercase
        if self.numbersCheck.isChecked():
            char_pool += string.digits
        if self.symbolsCheck.isChecked():
            char_pool += string.punctuation
        if not char_pool:
            self.passwordResult.setText("Error: Select at least one character set.")
            return
        password = "".join(random.choice(char_pool) for _ in range(length))
        self.passwordResult.setText(password)
    
    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.passwordResult.text())

# -------------------- Main Application Window -------------------- #
class MainWindow(QMainWindow):
    """
    The main window housing all tool tabs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Tool Utility Suite")
        self.setGeometry(100, 100, 900, 700)
        self.initUI()
    
    def initUI(self):
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(ImageConverterTab(), "Image Resizer/Converter")
        self.tabWidget.addTab(PDFMergerSplitterTab(), "PDF Merger/Splitter")
        self.tabWidget.addTab(ScreenshotOCRTab(), "Screenshot & OCR")
        self.tabWidget.addTab(ToDoListTab(), "To-Do List Manager")
        self.tabWidget.addTab(PasswordGeneratorTab(), "Password Generator")
        self.setCentralWidget(self.tabWidget)

# -------------------- Main Entry Point -------------------- #
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
