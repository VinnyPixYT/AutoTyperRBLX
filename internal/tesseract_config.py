import os
# Tesseract paths
TESSERACT_CMD = os.path.expandvars(r'%localappdata%\Programs\Tesseract-OCR\tesseract.exe')
TESSDATA_PREFIX = os.path.join(os.path.dirname(TESSERACT_CMD), 'tessdata')
