CREATE DATABASE FoodLabels_db;

USE FoodLabels_db;

CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL
);

CREATE TABLE Nutrition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    servings_size VARCHAR(100),
    servings_per_container VARCHAR(100),
    calories_per_serving VARCHAR(100),
    total_fat_amount VARCHAR(100),
    total_fat_dv VARCHAR(100),
    saturated_fat_amount VARCHAR(100),
    saturated_fat_dv VARCHAR(100),
    trans_fat_amount VARCHAR(100),
    trans_fat_dv VARCHAR(100),
    cholesterol_amount VARCHAR(100),
    cholesterol_dv VARCHAR(100),
    sodium_amount VARCHAR(100),
    sodium_dv VARCHAR(100),
    total_carbohydrates_amount VARCHAR(100),
    total_carbohydrates_dv VARCHAR(100),
    dietary_fiber_amount VARCHAR(100),
    dietary_fiber_dv VARCHAR(100),
    total_sugars_amount VARCHAR(100),
    total_sugars_dv VARCHAR(100),
    added_sugars_amount VARCHAR(100),
    added_sugars_dv VARCHAR(100),
    protein_amount VARCHAR(100),
    protein_dv VARCHAR(100),
    vitamin_d_amount VARCHAR(100),
    vitamin_d_dv VARCHAR(100),
    calcium_amount VARCHAR(100),
    calcium_dv VARCHAR(100),
    iron_amount VARCHAR(100),
    iron_dv VARCHAR(100),
    potassium_amount VARCHAR(100),
    potassium_dv VARCHAR(100)
);