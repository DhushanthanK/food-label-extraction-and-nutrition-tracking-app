from paddleocr import PaddleOCR
import re
import numpy as np
from rapidfuzz import fuzz, process

def extract_nutrition_info(image):
    """ocr on image"""
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(np.array(image), cls=True)

    def extract_row_lines(ocr_output, y_threshold=10):
        """extract info line by line"""
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

    def preprocess_text(text):
        """lowercase and eliminate spaces"""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())

    section_keywords = {
        "serving_info": ["Serving Size", "Servings per Container", "Servings per Package"],
        "calorie_info": ["Calories"],
        "nutrient_table": ["Total Fat", "Saturated Fat","Trans Fat", "Cholesterol", "Sodium", "Total Carbohydrates", "Dietary Fiber", "Total Sugars", "Added Sugars", "Protein", "Vitamin D", "Calcium", "Iron", "Potasium"]
    }

    priority_order = ["nutrient_table", "calorie_info", "serving_info"]

    def extract_section_fuzzy(row, threshold=85):
        """Detect section and categorize using fuzzy matching with priority resolution."""
        row_text = preprocess_text(" ".join(row))
        best_match = None
        best_score = 0
        detected_section = None

        for section in priority_order: 
            """Use priority order to resolve overlaps""" 
            for keyword in section_keywords[section]:
                score = fuzz.partial_ratio(row_text, preprocess_text(keyword))
                if score > best_score and score > threshold:
                    best_match = row
                    best_score = score
                    detected_section = section 

        if best_match:
            return (best_match, detected_section)
        return None

    serving_info, calorie_info, nutrient_table = [], [], []
    
    for row in rows:
        result = extract_section_fuzzy(row)
        if result:
            section = result[1]
            row_text = " ".join(result[0])
            if section == "serving_info":
                serving_info.append(row_text)
            elif section == "calorie_info":
                calorie_info.append(row_text)
            elif section == "nutrient_table":
                nutrient_table.append(row_text)

    def parse_general_info(text):
        """Regular expression to extract general info""" 
        patterns = [
                    (r"(serving size[:\s]*([\w\s/()]+))|([\w\s/()]+)\s*per serving|([\w\s/()]+)\s*per unit", "Serving Size"),
                    (r"(servings? per (container|package)[:\s]*(about\s)?(\d+))|((about\s)?(\d+)\s*servings? per (container|package))", "Servings per Container"),
                    (r"(calories[:\s]*(\d+))|(\d+)\s*calories per serving", "Calories")
                ]
        results = {}
        for pattern, category in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if category == "Serving Size":
                    results[category] = match.group(2) or match.group(3) or match.group(4)
                elif category == "Servings per Container":
                    results[category] = match.group(4) or match.group(7)
                elif category == "Calories":
                    results[category] = match.group(2) or match.group(3)
                if results[category]:
                    results[category] = results[category].strip().capitalize()
                    if category == "Serving Size" and results[category].lower() in ["amount", "per unit"]:
                        del results[category]
                    elif category == "Servings per Container" and results[category].lower() in ["about"]:
                        del results[category]
        return results

    nutrition_info = {}
    for text in serving_info + calorie_info:
        nutrition_info.update(parse_general_info(text))
    
    """Regular expression to extract amount and daily value with units""" 
    amount_regex = re.compile(r"(\d+(\.\d+)?\s*(g|mg|kcal|mcg))")  
    daily_value_regex = re.compile(r"(\d+(\.\d+)?\s*%)") 

    def parse_nutrient_line_fuzzy(text, threshold=75):
        """extrcat nutrition amount and daily value using fuzzy matching.""" 
        result = {"nutrient": None, "amount": None, "daily_value": None} 
        text = text.replace("Omg", "0mg").replace("Og", "0g").replace("O%", "0%")
        
        match, score, _ = process.extractOne(text, section_keywords['nutrient_table'], scorer=fuzz.partial_ratio)
        if score >= threshold:  
            if "Sugars" in text:
                if "Added" in text:
                    if "includes" in text or "included" in text:
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

    data = {
        "Serving Size": nutrition_info.get("Serving Size"),
        "Servings per Container": nutrition_info.get("Servings per Container"),
        "Calories": nutrition_info.get("Calories"),
    }

    for nutrient in section_keywords["nutrient_table"]:
        data[f"{nutrient} (Amount)"] = nutrient_info_dict.get(nutrient, {}).get("amount")
        data[f"{nutrient} (Daily Value)"] = nutrient_info_dict.get(nutrient, {}).get("daily_value")

    return data

# paddlepaddle             3.0.0b1
# paddleocr                2.9.1
# torch                    2.0.1
# torchaudio               2.0.2
# torchvision              0.15.2

