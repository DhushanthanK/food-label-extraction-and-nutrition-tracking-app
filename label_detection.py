# dataset link : https://universe.roboflow.com/lizazaza/nutrition-table

from inference_sdk import InferenceHTTPClient
import cv2
from PIL import Image

def crop_label(image_path):
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key="AuX83b3TUkz1802QnozK"
    )

    result = CLIENT.infer(image_path, model_id="nutrition-table/2")

    print("Result from API:", result)

    image = cv2.imread(image_path)
    if image is None:
        print("Failed to load the input image. Check the path.")
        exit(1)

    if 'predictions' in result and len(result['predictions']) > 0:
        for pred in result['predictions']:
            x, y, width, height = pred['x'], pred['y'], pred['width'], pred['height']

            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)

            image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            box = (x1, y1, x2, y2)
            cropped_image = image_pil.crop(box)
            return cropped_image
    else:
        print("No predictions found in the result.")
        return None
