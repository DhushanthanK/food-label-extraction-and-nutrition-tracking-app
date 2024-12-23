import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Nutrition Dashboard", page_icon="🍽️",layout="wide")

API_BASE_URL = "http://127.0.0.1:5000/api"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = None

def register_user(email, password):
    # Handle user registration via API call
    response = requests.post(f"{API_BASE_URL}/register", json={"email": email, "password": password})
    return response.json(), response.status_code

def login_user(email, password):
    # Handle user login via API call
    response = requests.post(f"{API_BASE_URL}/login", json={"email": email, "password": password})
    return response.json(), response.status_code

def upload_document(file):
    # Handle food label file upload to backend for OCR
    files = {"file": file}
    response = requests.post(f"{API_BASE_URL}/food_labels_db", files=files)
    return response.json(), response.status_code

def fetch_database_entries():
    # Fetch database entries from the backend
    response = requests.get(f"{API_BASE_URL}/food_labels_db")
    if response.status_code == 200:
        return pd.DataFrame(response.json()), response.status_code
    else:
        return None, response.status_code 

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Register", "Login"])

    with tab1:
        # Register Form
        st.header("Register 🔐")
        
        reg_email = st.text_input("Email", key="reg_email")
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if reg_email:
            if re.match(pattern, reg_email):
                st.success("Valid email format")
            else:
                reg_email = None
                st.error("Invalid email format. Please enter a valid email.")
            
        reg_password = st.text_input("Password", type="password", key="reg_password")
        pattern = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        if reg_password:
            if re.match(pattern, reg_password):
                st.success("Valid password format")
            else:
                reg_password = None
                st.error("Minimum eight characters, at least one letter, one number.")

        if st.button("Register"):
            result, status = register_user(reg_email, reg_password)
            if status == 201:
                st.success(result.get("message", "Registration successful"))
            else:
                st.error(result.get("message", "Registration failed"))
    
    with tab2:
        # Login Form
        st.header("Login 🗝")
        login_email = st.text_input("Email", key="login_email")
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if login_email:
            if not re.match(pattern, login_email):
                st.error("Invalid email format. Please enter a valid email.")

        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            result, status = login_user(login_email, login_password)
            if status == 200:
                st.session_state.logged_in = True
                st.session_state.email = login_email
                st.success("Logged in successfully!")
                st.rerun()  
            else:
                st.error(result.get("message", "Login failed"))

else:
    # When logged in
    tab1, tab2, tab3 = st.tabs(["Upload", "Dashboard", "Logout"])

    if "nutrition_data" not in st.session_state:
        st.session_state.nutrition_data, st.session_state.fetch_status = fetch_database_entries()
    with tab1:
        st.header("📄 Upload a Food Label Image 📝")

        uploaded_file = st.file_uploader("Please upload a Food Label below.", type=["jpg", "png", "pdf"])

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

            with st.spinner("Processing the file..."):
                result, status = upload_document(uploaded_file)

            if status == 200:
                st.success("File uploaded and processed successfully!") 

                new_data, new_status = fetch_database_entries()
                if new_status == 200:
                    st.session_state.nutrition_data = new_data
                    st.session_state.fetch_status = new_status
            else:
                st.error(f"Failed to upload or process the document: {result.get('message', '')}")

    with tab2:
        st.write("#")
        st.title("🌾🍀 Nutrition Dashboard 🍴🍇")

        data = st.session_state.nutrition_data
        status = st.session_state.fetch_status

        if status == 200 and not data.empty:
            nutrition_columns = [
                'id', 'servings_size', 'servings_per_container', 'calories_per_serving', 
                'total_fat_amount', 'total_fat_dv', 'saturated_fat_amount', 
                'saturated_fat_dv', 'trans_fat_amount', 'trans_fat_dv', 
                'cholesterol_amount', 'cholesterol_dv', 'sodium_amount', 
                'sodium_dv', 'total_carbohydrates_amount', 'total_carbohydrates_dv', 
                'dietary_fiber_amount', 'dietary_fiber_dv', 'total_sugars_amount', 
                'total_sugars_dv', 'added_sugars_amount', 'added_sugars_dv', 
                'protein_amount', 'protein_dv', 'vitamin_d_amount', 'vitamin_d_dv', 
                'calcium_amount', 'calcium_dv', 'iron_amount', 'iron_dv', 
                'potassium_amount', 'potassium_dv'
            ]

            nutrition_info = data[nutrition_columns] 
            latest_entry = nutrition_info.iloc[-1] 

            servings_size = latest_entry['servings_size']
            servings_per_container = latest_entry['servings_per_container']
            calories_per_serving = latest_entry['calories_per_serving']

            total_fat_amount = latest_entry['total_fat_amount']
            total_fat_dv = latest_entry['total_fat_dv']

            saturated_fat_amount = latest_entry['saturated_fat_amount']
            saturated_fat_dv = latest_entry['saturated_fat_dv']

            trans_fat_amount = latest_entry['trans_fat_amount']
            trans_fat_dv = latest_entry['trans_fat_dv']

            total_sugars_amount = latest_entry['total_sugars_amount']
            total_sugars_dv = latest_entry['total_sugars_dv']

            added_sugars_amount = latest_entry['added_sugars_amount']
            added_sugars_dv = latest_entry['added_sugars_dv']
            
            cholesterol_amount = latest_entry['cholesterol_amount']
            cholesterol_dv = latest_entry['cholesterol_dv']
            
            sodium_amount = latest_entry['sodium_amount']
            sodium_dv = latest_entry['sodium_dv']

            total_carbohydrates_amount = latest_entry['total_carbohydrates_amount']
            total_carbohydrates_dv = latest_entry['total_carbohydrates_dv']

            dietary_fiber_amount = latest_entry['dietary_fiber_amount']
            dietary_fiber_dv = latest_entry['dietary_fiber_dv']

            protein_amount = latest_entry['protein_amount']
            protein_dv = latest_entry['protein_dv']

            vitamin_d_amount = latest_entry['vitamin_d_amount']
            vitamin_d_dv = latest_entry['vitamin_d_dv']

            calcium_amount = latest_entry['calcium_amount']
            calcium_dv = latest_entry['calcium_dv']

            iron_amount = latest_entry['iron_amount']
            iron_dv = latest_entry['iron_dv']

            potassium_amount = latest_entry['potassium_amount']
            potassium_dv = latest_entry['potassium_dv']

            def get_display_value(value):
                return value if value not in [None, ""] else "0%"

            def get_delta_color_least_preferred(value):
                if value is None or value.strip() == "":
                    return "black", "#e0e0e0" 
                numeric_value = float(value.strip('%'))
                if numeric_value > 20:
                    return "red", "#ffcccc"  
                return "green", "#ccffcc"  

            def get_delta_color_most_preferred(value):
                if value is None or value.strip() == "":
                    return "black", "#e0e0e0"  
                numeric_value = float(value.strip('%'))
                if numeric_value < 5:
                    return "red", "#ffcccc"  
                return "green", "#ccffcc" 

            with st.container():
                st.write("#")
                st.subheader("📌 General Information ⚡")
                st.markdown("***")
                a, b, c = st.columns(3)
                
                a.markdown(f"""
                    <div style="font-size: 24px; font-weight: bold; color: white; background-color: #3498db; border: 2px solid #2980b9; padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="margin: 0;">Serving Size</p>
                        <p style="font-size: 32px; font-weight: bold; color: white; margin-top: 10px;">{get_display_value(servings_size)}</p>
                    </div>
                """, unsafe_allow_html=True)

                b.markdown(f"""
                    <div style="font-size: 24px; font-weight: bold; color: white; background-color: #3498db; border: 2px solid #2980b9; padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="margin: 0;">Servings Per Container</p>
                        <p style="font-size: 32px; font-weight: bold; color: white; margin-top: 10px;">{get_display_value(servings_per_container)}</p>
                    </div>
                """, unsafe_allow_html=True)

                c.markdown(f"""
                    <div style="font-size: 24px; font-weight: bold; color: white; background-color: #3498db; border: 2px solid #2980b9; padding: 20px; border-radius: 10px; text-align: center;">
                        <p style="margin: 0;">Calories Per Serving</p>
                        <p style="font-size: 32px; font-weight: bold; color: white; margin-top: 10px;">{get_display_value(calories_per_serving)}</p>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                <style>
                    div[data-testid="stMetricValue"] {
                        font-size: 32px;
                        font-weight: bold;
                        color: white;
                        background-color: #3498db;
                        border: 2px solid #2980b9;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                    }
                </style>
            """, unsafe_allow_html=True)

            def create_boxed_html(title, amount, percentage, color, box_color):
                return f"""
                <div style='border: 2px solid #d3d3d3; border-radius: 10px; padding: 20px; text-align: center; background-color: {box_color};'>
                    <p style='color:black; font-size: 20px; font-weight: bold; margin: 0;'>{title}</p>
                    <p style='color:black; font-size: 24px; font-weight: normal; margin-top: 10px;'>{amount}</p>
                    <p style='color:{color}; font-size: 22px; font-weight: bold; margin-top: 10px;'>{percentage}</p>
                </div>
                """
            
            with st.container():
                st.write("#")
                st.subheader("⚠️ Least Preferred Ingredients 🚫")
                st.markdown("***")
                d, e, f, g, h, i, j = st.columns(7)

                with d:
                    text_color, box_color = get_delta_color_least_preferred(total_fat_dv)
                    st.markdown(
                        create_boxed_html(
                            "Total Fat",
                            f"{total_fat_amount}",
                            f"({get_display_value(total_fat_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with e:
                    text_color, box_color = get_delta_color_least_preferred(saturated_fat_dv)
                    st.markdown(
                        create_boxed_html(
                            "Saturated Fat",
                            f"{saturated_fat_amount}",
                            f"({get_display_value(saturated_fat_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with f:
                    text_color, box_color = get_delta_color_least_preferred(trans_fat_dv)
                    st.markdown(
                        create_boxed_html(
                            "Trans Fat",
                            f"{trans_fat_amount}",
                            f"({get_display_value(trans_fat_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with g:
                    text_color, box_color = get_delta_color_least_preferred(total_sugars_dv)
                    st.markdown(
                        create_boxed_html(
                            "Total Sugars",
                            f"{total_sugars_amount}",
                            f"({get_display_value(total_sugars_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with h:
                    text_color, box_color = get_delta_color_least_preferred(added_sugars_dv)
                    st.markdown(
                        create_boxed_html(
                            "Added Sugars",
                            f"{added_sugars_amount}",
                            f"({get_display_value(added_sugars_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with i:
                    text_color, box_color = get_delta_color_least_preferred(cholesterol_dv)
                    st.markdown(
                        create_boxed_html(
                            "Cholesterol",
                            f"{cholesterol_amount}",
                            f"({get_display_value(cholesterol_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with j:
                    text_color, box_color = get_delta_color_least_preferred(sodium_dv)
                    st.markdown(
                        create_boxed_html(
                            "Sodium",
                            f"{sodium_amount}",
                            f"({get_display_value(sodium_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )

            with st.container():
                st.write("#")
                st.subheader("✅ Most Preferred Ingredients 🎖")
                st.markdown("***")
                k, l, m, n, o, p, q = st.columns(7)

                with k:
                    text_color, box_color = get_delta_color_most_preferred(total_carbohydrates_dv)
                    st.markdown(
                        create_boxed_html(
                            "Total Carbs",
                            f"{total_carbohydrates_amount}",
                            f"({get_display_value(total_carbohydrates_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with l:
                    text_color, box_color = get_delta_color_most_preferred(dietary_fiber_dv)
                    st.markdown(
                        create_boxed_html(
                            "Dietary Fiber",
                            f"{dietary_fiber_amount}",
                            f"({get_display_value(dietary_fiber_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with m:
                    text_color, box_color = get_delta_color_most_preferred(protein_dv)
                    st.markdown(
                        create_boxed_html(
                            "Protein",
                            f"{protein_amount}",
                            f"({get_display_value(protein_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with n:
                    text_color, box_color = get_delta_color_most_preferred(vitamin_d_dv)
                    st.markdown(
                        create_boxed_html(
                            "Vitamin D",
                            f"{vitamin_d_amount}",
                            f"({get_display_value(vitamin_d_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with o:
                    text_color, box_color = get_delta_color_most_preferred(calcium_dv)
                    st.markdown(
                        create_boxed_html(
                            "Calcium",
                            f"{calcium_amount}",
                            f"({get_display_value(calcium_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with p:
                    text_color, box_color = get_delta_color_most_preferred(iron_dv)
                    st.markdown(
                        create_boxed_html(
                            "Iron",
                            f"{iron_amount}",
                            f"({get_display_value(iron_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                with q:
                    text_color, box_color = get_delta_color_most_preferred(potassium_dv)
                    st.markdown(
                        create_boxed_html(
                            "Potassium",
                            f"{potassium_amount}",
                            f"({get_display_value(potassium_dv)})",
                            text_color,
                            box_color
                        ),
                        unsafe_allow_html=True,
                    )
                    
            def convert_to_float(value):
                # Convert a percentage string (e.g., '15%') to a float.
                try:
                    return float(value.strip('%')) if value not in [None, ""] else 0
                except ValueError:
                    return 0
                
            data = {
                "Nutrient": [
                    "Total Fat", "Saturated Fat", "Trans Fat", "Total Sugars",
                    "Added Sugars", "Cholesterol", "Sodium", "Total Carbohydrates",
                    "Dietary Fiber", "Protein", "Vitamin D", "Calcium", "Iron", "Potassium"
                ],
                "Daily Value (%)": [
                    total_fat_dv, saturated_fat_dv, trans_fat_dv, total_sugars_dv,
                    added_sugars_dv, cholesterol_dv, sodium_dv, total_carbohydrates_dv,
                    dietary_fiber_dv, protein_dv, vitamin_d_dv, calcium_dv,
                    iron_dv, potassium_dv
                ]
            }

            df = pd.DataFrame(data)
            df["Daily Value (%)"] = df["Daily Value (%)"].apply(convert_to_float)

            st.write("#")
            st.subheader("📉 Nutrition Daily Values (%)📊")
            st.markdown("***")

            fig = px.bar(df,
             x="Daily Value (%)",
             y="Nutrient",
             orientation='h',
             color="Daily Value (%)",  
             color_continuous_scale="Inferno", 
             labels={"Daily Value (%) ": "Daily Values (%)", "Nutrient": "Nutrient"},
             text="Daily Value (%)")  

            fig.update_layout(
                showlegend=False, 
                xaxis_title="",
                yaxis_title="",
                plot_bgcolor='white', 
                xaxis=dict(showgrid=False),  
                yaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig)

            st.subheader("📉 Nutrition Information Table 📊")
            st.markdown("***")
            
            st.dataframe(nutrition_info) 

        else:
            st.error("Failed to fetch data from the database or no entries available.")

    with tab3:
        st.header("🔒 Logout")
        st.write("Click the button below to logout.")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.email = None
            st.success("Logged out successfully!")
            st.rerun()  