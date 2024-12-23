import cv2
import re
from paddleocr import PaddleOCR
from rapidfuzz import fuzz, process
import pandas as pd

def extract_nutrition_info(img_path):
    # Initialize OCR model
    ocr = PaddleOCR(use_angle_cls=True, lang='en')

    # Load image
    img = cv2.imread(img_path)

    # Extract text using OCR
    result = ocr.ocr(img_path, cls=True)

    # Function to preprocess text
    def preprocess_text(text):
        """Clean and preprocess text for consistent processing."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())

    # Extract rows based on OCR result bounding box positions
    def extract_row_lines(ocr_output, y_threshold=10):
        """
        Extracts row lines from PaddleOCR output based on bounding box positions and thresholds.
        """
        rows = []
        current_row = []
        row_center = None

        for box in ocr_output:
            top_left_y = box[0][0][1]
            bottom_left_y = box[0][3][1]
            cell_center_y = (top_left_y + bottom_left_y) / 2

            if row_center is None:
                row_center = cell_center_y

            if abs(row_center - cell_center_y) > y_threshold:
                if current_row:
                    rows.append(current_row)
                row_center = cell_center_y
                current_row = [box[1][0]]
            else:
                current_row.append(box[1][0])

        if current_row:
            rows.append(current_row)

        return rows

    ocr_output = result[0]
    rows = extract_row_lines(ocr_output)

    # Keywords for section detection
    section_keywords = {
        "serving_info": ["Serving Size", "Servings per container", "Servings per package"],
        "calorie_info": ["Calories"],
        "nutrient_table": ["Total Fat", "Saturated Fat", "Trans Fat", "Cholesterol", "Sodium", "Total Carbohydrates", 
                           "Dietary Fiber", "Total Sugars", "Added Sugars", "Protein", "Vitamin D", "Calcium", "Iron", "Potassium"]
    }
    
    priority_order = ["nutrient_table", "calorie_info", "serving_info"]

    # Fuzzy matching to detect section
    def extract_section_fuzzy(row, threshold=85):
        """Detect section using fuzzy matching with priority resolution."""
        row_text = preprocess_text(" ".join(row))
        best_match = None
        best_score = 0
        detected_section = None

        for section in priority_order:
            for keyword in section_keywords[section]:
                score = fuzz.partial_ratio(row_text, preprocess_text(keyword))
                if score > best_score and score > threshold:
                    best_match = row
                    best_score = score
                    detected_section = section

        if best_match:
            return (best_match, detected_section)
        return None

    serving_info = []
    calorie_info = []
    nutrient_table = []

    for row in rows:
        result = extract_section_fuzzy(row)
        if result:
            if result[1] == "serving_info":
                serving_info.append(" ".join(result[0]))
            elif result[1] == "calorie_info":
                calorie_info.append(" ".join(result[0]))
            elif result[1] == "nutrient_table":
                nutrient_table.append(" ".join(result[0]))

    # Parsing general information like Serving Size, Servings per Container, and Calories
    def parse_general_info(text):
        patterns = [
            (r"(serving size[:\s]*([\w\s/()]+))|([\w\s/()]+)\s*per serving|([\w\s/()]+)\s*per unit", "Serving Size"),
            (r"(servings? per (container|package)[:\s]*(about\s)?(\d+))|((about\s)?(\d+)\s*servings? per (container|package))", "Servings per container"),
            (r"(calories[:\s]*(\d+))|(\d+)\s*calories per serving", "Calories")
        ]
        
        results = {}

        for pattern, category in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if category == "Serving Size":
                    results[category] = match.group(2) or match.group(3) or match.group(4)
                elif category == "Servings per container":
                    results[category] = match.group(4) or match.group(7)
                elif category == "Calories":
                    results[category] = match.group(2) or match.group(3)

                if results[category]:
                    results[category] = results[category].strip().capitalize()

                    if category == "Serving Size" and results[category].lower() in ["amount", "per unit"]:
                        del results[category]
                    elif category == "Servings per container" and results[category].lower() in ["about"]:
                        del results[category]
        return results

    # Parsing nutrient information
    amount_regex = re.compile(r"(\d+(\.\d+)?\s*(g|mg|kcal|mcg))")
    daily_value_regex = re.compile(r"(\d+(\.\d+)?\s*%)")

    def parse_nutrient_line_fuzzy(text, threshold=75):
        result = {"nutrient": None, "amount": None, "daily_value": None}

        text = text.replace("Omg", "0mg").replace("Og", "0g").replace("O%", "0%")

        match, score, _ = process.extractOne(text, section_keywords['nutrient_table'], scorer=fuzz.partial_ratio)
        if score >= threshold:
            if "Sugars" in text:
                if "Added" in text:
                    if "includes" in text or "included" in text or "in" in text:
                        result["nutrient"] = None
                    else:
                        result["nutrient"] = "Added Sugars"
                else:
                    result["nutrient"] = "Total Sugars"
            else:
                result["nutrient"] = match

        amount_match = amount_regex.search(text)
        if amount_match:
            result["amount"] = amount_match.group(1).strip()

        daily_value_match = daily_value_regex.search(text)
        if daily_value_match:
            result["daily_value"] = daily_value_match.group(1).strip()

        return result

    nutrient_info_dict = {}

    for line in nutrient_table:
        nutrient_info = parse_nutrient_line_fuzzy(line)
        if nutrient_info["nutrient"]:
            nutrient_info_dict[nutrient_info["nutrient"]] = nutrient_info

    # Final structured data
    data = {}

    # Process Serving and Calorie info
    for text in serving_info + calorie_info:
        result = parse_general_info(text)
        if result:
            for key, value in result.items():
                data[key] = value

    # Add Nutrient Info
    for nutrient in section_keywords["nutrient_table"]:
        data[f"{nutrient} (Amount)"] = nutrient_info_dict.get(nutrient, {}).get("amount")
        data[f"{nutrient} (Daily Value)"] = nutrient_info_dict.get(nutrient, {}).get("daily_value")

    return data