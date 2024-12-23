-- Create FoodLabels database
CREATE DATABASE IF NOT EXISTS FoodLabels;

-- Use the created database
USE FoodLabels;

-- Create User table
CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL
);

-- Create Nutrition table
CREATE TABLE IF NOT EXISTS Nutrition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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