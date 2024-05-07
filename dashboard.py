import streamlit as st
import requests
import plotly.graph_objects as go
# Define the Streamlit app
def main():
    # Title and description
    st.title("Loan Eligibility Dashboard")
    st.markdown("This dashboard helps client advisors assess the probability of loan eligibility based on a client's profile.")

    # Input form for client data
    st.sidebar.header("Client Profile")
    code_gender = {"Male": "M", "Female": "F"}[st.sidebar.selectbox("Gender", ["Male", "Female"])]
    flag_own_car = {"Yes": "Y", "No": "N"}[st.sidebar.selectbox("Owns a Car", ["Yes", "No"])]
    organization_type = st.sidebar.selectbox("Organization Type", [
        'Advertising', 'Agriculture', 'Bank', 'Business Entity Type 1', 'Business Entity Type 2', 'Business Entity Type 3', 
        'Cleaning', 'Construction', 'Culture', 'Electricity', 'Emergency', 'Government', 'Hotel', 'Housing', 'Industry: type 1',
        'Industry: type 2', 'Industry: type 3', 'Industry: type 4', 'Industry: type 5', 'Industry: type 6', 'Industry: type 7', 
        'Industry: type 8', 'Industry: type 9', 'Industry: type 10', 'Industry: type 11', 'Industry: type 12', 'Industry: type 13', 
        'Insurance', 'Kindergarten', 'Legal Services', 'Medicine', 'Military', 'Mobile', 'Other', 'Police', 'Postal', 'Realtor', 
        'Religion', 'Restaurant', 'School', 'Security', 'Security Ministries', 'Self-employed', 'Services', 'Telecom', 
        'Trade: type 1', 'Trade: type 2', 'Trade: type 3', 'Trade: type 4', 'Trade: type 5', 'Trade: type 6', 'Trade: type 7', 
        'Transport: type 1', 'Transport: type 2', 'Transport: type 3', 'Transport: type 4', 'University', 'XNA'
    ])
    from datetime import datetime, date

    # Get the current date as a date object
    current_date = date.today()
    # Display a date input widget to select the client's birthdate
    birth_date = st.sidebar.date_input("Client's Birthdate", value=datetime(1990, 1, 1))
    # Convert birth_date to datetime object
    birth_datetime = datetime.combine(birth_date, datetime.min.time())
    # Calculate the age in days
    days_birth = (current_date - birth_datetime.date()).days

    days_id_publish = st.sidebar.number_input("ID Document Update (Days Ago)", value=0)
    sk_id_curr = st.sidebar.number_input("Client ID (6 digits)", min_value=100000, max_value=999999, value=100000)
    reg_city_not_live_city = {"Yes": 1, "No": 0}[st.sidebar.selectbox("Is the client's permanent adress the same as his contact adress?", ["Yes", "No"])]
    ext_source_1 = st.sidebar.slider("Credit Score 1", min_value=0.0, max_value=1.0, value=0.5)
    ext_source_2 = st.sidebar.slider("Credit Score 2", min_value=0.0, max_value=1.0, value=0.5)
    ext_source_3 = st.sidebar.slider("Credit Score 3", min_value=0.0, max_value=1.0, value=0.5)
    years_beginexpluatation_mode = st.sidebar.slider("Years of Residence Score", min_value=0.0, max_value=1.0, value=0.5)
    commonarea_mode = st.sidebar.slider("Common Area State Score", min_value=0.0, max_value=1.0, value=0.5)
    floorsmax_mode = st.sidebar.slider("Number of Floors Score", min_value=0.0, max_value=1.0, value=0.5)
    livingapartments_mode = st.sidebar.slider("Apartment Size Score", min_value=0.0, max_value=1.0, value=0.5)
    years_build_medi = st.sidebar.slider("Building Age Score", min_value=0.0, max_value=1.0, value=0.5)

    # Create a dictionary with the client data
    client_data = {
        "CODE_GENDER": code_gender,
        "FLAG_OWN_CAR": flag_own_car,
        "ORGANIZATION_TYPE": organization_type,
        "DAYS_BIRTH": -days_birth,
        "DAYS_ID_PUBLISH": -days_id_publish,
        "SK_ID_CURR": sk_id_curr,
        "REG_CITY_NOT_LIVE_CITY": reg_city_not_live_city,
        "EXT_SOURCE_1": ext_source_1,
        "EXT_SOURCE_2": ext_source_2,
        "EXT_SOURCE_3": ext_source_3,
        "YEARS_BEGINEXPLUATATION_MODE": years_beginexpluatation_mode,
        "COMMONAREA_MODE": commonarea_mode,
        "FLOORSMAX_MODE": floorsmax_mode,
        "LIVINGAPARTMENTS_MODE": livingapartments_mode,
        "YEARS_BUILD_MEDI": years_build_medi
    }

    # Make a request to the FastAPI endpoint
    response = requests.post('https://mysterious-anchorage-08977-5847c69ff008.herokuapp.com/predict_proba', json=client_data)

    # Display the prediction result
    if response.status_code == 200:
        prediction = response.json()["prediction"]
        st.success(f"Loan Eligibility Score: {prediction}")
       # Plot the gauge chart without delta
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prediction,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Loan Eligibility", 'font': {'size': 30}},
            gauge={
                'shape': "angular",
                'axis': {'range': [None, 1], 'tickwidth': 1, 'tickcolor': "#fffef5"},
                'bgcolor': "#fffef5",
                'borderwidth': 0,
                'bordercolor': "rgba(0,0,0,0)",
                'steps': [
                {'range': [0, 0.195], 'color': '#f13c0b'},
                {'range': [0.195, 0.205], 'color': '#fffef5'},
                {'range': [0.205, 0.395], 'color': '#fe7900'},
                {'range': [0.395, 0.405], 'color': '#fffef5'},
                {'range': [0.405, 0.595], 'color': '#ffcf15'},
                {'range': [0.595, 0.605], 'color': '#fffef5'},
                {'range': [0.605, 0.795], 'color': '#88c817'},
                {'range': [0.795, 0.805], 'color': '#fffef5'},
                {'range': [0.805, 1], 'color': '#01bf11'}
                ],
                'threshold': {
                    'line': {'color': "grey", 'width': 4},
                    'thickness': 0.8,
                    'value': prediction
                }
            }
        ))

        # Remove the fill of the gauge
        fig['data'][0]['gauge']['bar']['color'] = "rgba(0,0,0,0)"

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to get prediction from server.")

# Run the app
if __name__ == "__main__":
    main()
