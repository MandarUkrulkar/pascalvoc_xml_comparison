# Annotation Comparison Tool

This is a **Streamlit-based web application** designed to compare annotation files (in Pascal VOC XML format) between two folders. It helps visualize and analyze matching and non-matching bounding boxes between two different sets of annotations, along with the associated class names.

## Features

- Compare annotations between two folders.
- Detect and count:
  - Matching bounding boxes (with >50% overlap).
  - Unmatched bounding boxes.
  - Class mismatches for matched boxes.
- Visualize matched/unmatched annotations side-by-side.
- List unique detections found only in one folder.
- Interactive selection of unmatched entries for image + bounding box visualization.

## Requirements

- Python 3.7+
- Streamlit
- pandas
- Pillow
- matplotlib

## usage
streamlit run app.py
Open your browser and go to http://localhost:8501.

Input:

Path to Folder 1 (annotations in XML format).

Path to Folder 2 (annotations in XML format).

Path to the image folder (images corresponding to the XMLs).

Review the comparison results and use the slider to visualize mismatches.

##Folder structrue
your_dataset/
├── images/
│   ├── image1.jpg
│   └── image2.jpg
├── folder1_annotations/
│   ├── image1.xml
│   └── image2.xml
└── folder2_annotations/
    ├── image1.xml
    └── image2.xml


