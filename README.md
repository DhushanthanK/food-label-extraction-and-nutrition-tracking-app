# food-label-extraction-and-nutrition-tracking-app
This streamlit based web app allows users to upload a food label image and extract text using PaddleOCR and then extract serving, calories and nutrition information using Regex and Fuzzy matching.

## Features
- **User Authentication**: Allows user accounts with email and hashed passwords.
- **Image Upload**: Users can upload food label images.
- **Text Extraction**: Extract text from food labels using PaddleOCR.
- **Information Parsing**: Extract serving size, calories, and nutritional information from text using Regex and Fuzzy matching.
- **Streamlit Interface**: A user-friendly front-end for uploading images and viewing extracted information.
- **Detailed Storage**: Save extracted nutritional data in a structured format within the database.

## Project Structure
- **app.py**: Flask backend for handling API requests and managing server-side logic.
- **ocr.py**: Extracts text using PaddleOCR and then extracts serving size, calories, and nutritional information using Regex and Fuzzy matching.
- **streamlit.py**: Streamlit front-end for the user interface, allowing users to upload images and view extracted information.
- **query.sql**: SQL query to create the database and tables for storing user and nutritional information.

## Setup Instructions

1. Clone this repository.

```bash
  git clone https://github.com/DhushanthanK/food-label-extraction-and-nutrition-tracking-app.git
```

2. Navigate to the Project Directory.

```bash
  cd <path-to-project-directory>
```

3. create a `.env` file.

```
DATABASE_USER="username"
DATABASE_PASSWORD="password"
DATABASE_HOST="host"
DATABASE_NAME=FoodLabels_db
```

4. Create the virtual environment.

```bash
python -m venv venv
source venv\bin\activate
```

5. Install the requirements.

```bash
pip install -r requirements.txt
```

5. Run SQL Query in MySQL to create database.

```
mysql -u <username> -p query.sql
```

6. run the flask back-end.

```bash
python app.py
```
8. run the streamlit front-end.

```bash
streamlit run streamlit.py
```

## License

This project is licensed under the MIT License.
