
import os
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    annotations = []
    for obj in root.findall('.//object'):
        name = obj.find('name').text
        bbox_elem = obj.find('bndbox')
        bbox = [
            float(bbox_elem.find(coord).text) for coord in ['xmin', 'ymin', 'xmax', 'ymax']
        ]
        annotations.append({'filename': os.path.basename(xml_path), 'name': name, 'bbox': bbox})

    return annotations

def compare_annotations(folder1, folder2):
    matching_bbox_count = 0
    unmatched_bbox_count_folder1 = 0
    unmatched_bbox_count_folder2 = 0
    unmatched_data = []
    matched_data = []

    total_annotations_folder1 = 0
    total_annotations_folder2 = 0
    total_bboxes_folder1 = 0
    total_bboxes_folder2 = 0

    for file1 in os.listdir(folder1):
        if file1.endswith('.xml'):
            xml_path1 = os.path.join(folder1, file1)
            annotation1 = parse_xml(xml_path1)
            total_annotations_folder1 += 1
            total_bboxes_folder1 += len(annotation1)

            corresponding_xml_path2 = os.path.join(folder2, file1)
            if os.path.exists(corresponding_xml_path2):
                annotation2 = parse_xml(corresponding_xml_path2)
                total_annotations_folder2 += 1
                total_bboxes_folder2 += len(annotation2)

                for ann1 in annotation1:
                    bbox1 = ann1['bbox']
                    match_found = False

                    for ann2 in annotation2:
                        bbox2 = ann2['bbox']
                        overlap = overlap_percentage(bbox1, bbox2)

                        if overlap > 50:
                            matching_bbox_count += 1
                            match_found = True

                            if ann1['name'] != ann2['name']:
                                unmatched_data.append({'filename': ann1['filename'], 'Box Coordinates': bbox1, 'Class Folder1': ann1['name'], 'Class Folder2': ann2['name']})
                            else:
                                matched_data.append({'filename': ann1['filename'], 'Box Coordinates': bbox1, 'Class Name': ann1['name']})
                                break

                    if not match_found:
                        unmatched_bbox_count_folder1 += 1

    unmatched_bbox_count_folder2 = abs(total_bboxes_folder2 - matching_bbox_count)

    return matching_bbox_count, unmatched_bbox_count_folder1, unmatched_bbox_count_folder2, unmatched_data, matched_data, total_annotations_folder1, total_annotations_folder2, total_bboxes_folder1, total_bboxes_folder2

def overlap_percentage(box1, box2):
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2

    overlap_x = max(0, min(x2, x4) - max(x1, x3))
    overlap_y = max(0, min(y2, y4) - max(y1, y3))

    overlap_area = overlap_x * overlap_y
    area_box1 = (x2 - x1) * (y2 - y1)
    area_box2 = (x4 - x3) * (y4 - y3)

    overlap_percentage = (overlap_area / min(area_box1, area_box2)) * 100

    return overlap_percentage

def display_images_with_bboxes(image_folder, df, selected_index):
    if selected_index < len(df):
        row = df.iloc[selected_index]
        xml_name = row['filename']
        image_name = os.path.splitext(xml_name)[0] + ".jpg"  # Change the extension to .jpg
        image_path = os.path.join(image_folder, image_name)

        img = Image.open(image_path)
        img_width, img_height = img.size

        fig, ax = plt.subplots(1, 2, figsize=(18, 9))

        # Left plot: Bounding boxes and classes from Folder 1
        ax[0].imshow(img)
        ax[0].set_title(f'Annotations from Folder 1: {image_name}')

        for _, bbox_data in df[df['filename'] == xml_name].iterrows():
            bbox = bbox_data['Box Coordinates']
            class_name = bbox_data['Class Folder1']

            x, y, w, h = bbox
            rect = patches.Rectangle((x, y), w - x, h - y, linewidth=1, edgecolor='r', facecolor='none', label=class_name)
            ax[0].add_patch(rect)
            ax[0].text(x, y - 5, class_name, color='r')

        # Right plot: Bounding boxes from Folder 2, classes from Folder 2
        ax[1].imshow(img)
        ax[1].set_title(f'Annotations from Folder 2: {image_name}')

        for _, bbox_data in df[df['filename'] == xml_name].iterrows():
            bbox = bbox_data['Box Coordinates']
            class_name = bbox_data['Class Folder2']

            x, y, w, h = bbox
            rect = patches.Rectangle((x, y), w - x, h - y, linewidth=1, edgecolor='b', facecolor='none', label=class_name)
            ax[1].add_patch(rect)
            ax[1].text(x, y - 5, class_name, color='b')

        st.pyplot(fig)

def main():
    st.title("Annotation Comparison Tool")

    folder1 = st.text_input("Enter path to folder 1 (annotations):", "")
    folder2 = st.text_input("Enter path to folder 2 (annotations):", "")
    image_folder = st.text_input("Enter path to image folder:", "")

    if os.path.exists(folder1) and os.path.exists(folder2) and os.path.exists(image_folder):
        matching_bbox_count, unmatched_bbox_count_folder1, unmatched_bbox_count_folder2, unmatched_data, matched_data, total_annotations_folder1, total_annotations_folder2, total_bboxes_folder1, total_bboxes_folder2 = compare_annotations(folder1, folder2)

        st.write("Comparison Results:")
        st.write(f"Total Annotations in Folder 1: {total_annotations_folder1}")
        st.write(f"Total Annotations in Folder 2: {total_annotations_folder2}")
        st.write(f"Total Bounding Boxes in Folder 1: {total_bboxes_folder1}")
        st.write(f"Total Bounding Boxes in Folder 2: {total_bboxes_folder2}")
        st.write(f"Matching Bounding Boxes: {matching_bbox_count}")
        st.write(f"Unique Bounding Boxes in Folder 1: {unmatched_bbox_count_folder1}")
        st.write(f"Unique Bounding Boxes in Folder 2: {unmatched_bbox_count_folder2}")

        if matched_data:
            st.write(f"Detailed Comparison - Matching Bounding Boxes with Matched classes : {len(matched_data)}")
            df_matched = pd.DataFrame(matched_data)
            st.write(df_matched)

        if unmatched_data:
            st.write(f"Detailed Comparison - Matching Bounding Boxes with Unmatched classes : {len(unmatched_data)}")
            df_unmatched = pd.DataFrame(unmatched_data)
            st.write(df_unmatched)

        # Identify unique detections in folder 1
        unique_detections_folder1 = []
        for file1 in os.listdir(folder1):
            if file1.endswith('.xml'):
                xml_path1 = os.path.join(folder1, file1)
                annotation1 = parse_xml(xml_path1)
                corresponding_xml_path2 = os.path.join(folder2, file1)

                if not os.path.exists(corresponding_xml_path2):
                    unique_detections_folder1.extend(annotation1)
                else:
                    annotation2 = parse_xml(corresponding_xml_path2)

                    for ann1 in annotation1:
                        unique_bbox = True
                        for ann2 in annotation2:
                            if overlap_percentage(ann1['bbox'], ann2['bbox']) > 50:
                                unique_bbox = False
                                break
                        if unique_bbox:
                            unique_detections_folder1.append(ann1)

        df_unique_folder1 = pd.DataFrame(unique_detections_folder1)
        if not df_unique_folder1.empty:
            st.write(f"Unique Detections in Folder 1: {len(df_unique_folder1)}")
            st.write(df_unique_folder1)
            
        

        # Similarly, identify unique detections in folder 2 using the same logic
        
        
        # Identify unique detections in folder 2
        unique_detections_folder2 = []
        for file2 in os.listdir(folder2):
            if file2.endswith('.xml'):
                xml_path2 = os.path.join(folder2, file2)
                annotation2 = parse_xml(xml_path2)
                corresponding_xml_path1 = os.path.join(folder1, file2)

                if not os.path.exists(corresponding_xml_path1):
                    unique_detections_folder2.extend(annotation2)
                else:
                    annotation1 = parse_xml(corresponding_xml_path1)

                    for ann2 in annotation2:
                        unique_bbox = True
                        for ann1 in annotation1:
                            if overlap_percentage(ann2['bbox'], ann1['bbox']) > 50:
                                unique_bbox = False
                                break
                        if unique_bbox:
                            unique_detections_folder2.append(ann2)

        df_unique_folder2 = pd.DataFrame(unique_detections_folder2)
        if not df_unique_folder2.empty:
            st.write(f"Unique Detections in Folder 2: {len(df_unique_folder2)}")
            st.write(df_unique_folder2)


    else:
        st.error("Invalid folder paths. Please provide valid paths.")

    # Slider for selecting the file pair to display
    matching_bbox_count, unmatched_bbox_count_folder1, unmatched_bbox_count_folder2, unmatched_data, matched_data, total_annotations_folder1, total_annotations_folder2, total_bboxes_folder1, total_bboxes_folder2 = compare_annotations(folder1, folder2)

    df_matched = pd.DataFrame(matched_data)
    df_unmatched = pd.DataFrame(unmatched_data)

    if len(df_unmatched) > 0:
        selected_index = st.slider("Select File Pair", 0, len(df_unmatched) - 1, 0)
        display_images_with_bboxes(image_folder, df_unmatched, selected_index)

if __name__ == "__main__":
    main()
