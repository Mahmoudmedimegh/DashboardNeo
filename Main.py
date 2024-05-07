import streamlit as st
import pandas as pd
import requests
from sklearn.base import BaseEstimator, TransformerMixin
import plotly.graph_objects as go

def anonymize_birth(days_birth):
    age = -days_birth // 365
    return f"{(age // 10) * 10}s"

def categorize_publish_days(days_id_publish):
    if days_id_publish < -3650:
        return '> 10 years'
    elif days_id_publish < -1825:
        return '5-10 years'
    elif days_id_publish < -365:
        return '1-5 years'
    else:
        return '< 1 year'
def categorize_org_type(org_type):
    # Education
    if org_type in ['Kindergarten', 'School', 'University']:
        return 'Education'
    
    # Self-Employment
    elif org_type == 'Self-employed':
        return 'Freelance'
    
    # Government and Public Services
    elif org_type in ['Government', 'Military', 'Police', 'Security Ministries', 'Postal', 'Emergency']:
        return 'Government'
    
    # Health and Social Work
    elif org_type in ['Medicine', 'Social Services']:
        return 'Healthcare'
    
    # Financial Services
    elif org_type in ['Bank', 'Insurance', 'Legal Services']:
        return 'Finance'
    
    # Trade and Retail
    elif 'Trade: type' in org_type or org_type == 'Realtor':
        return 'Retail'
    
    # Transportation and Communication
    elif 'Transport: type' in org_type or org_type == 'Telecom':
        return 'Logistics'
    
    # Utilities and Infrastructure
    elif org_type == 'Electricity' or 'Water Supply' in org_type or 'Waste Management' in org_type:
        return 'Utilities'
    
    # Manufacturing and Industry
    elif 'Industry: type' in org_type or org_type == 'Construction':
        return 'Industry'
    
    # Hospitality and Leisure
    elif org_type in ['Restaurant', 'Hotel']:
        return 'Hospitality'
    
    # Professional Services
    elif org_type in ['Advertising', 'Cleaning', 'Services', 'Security']:
        return 'Services'
    
    # Agriculture and Natural Resources
    elif org_type == 'Agriculture':
        return 'Agriculture'
    
    # Information and Technology
    elif org_type in ['IT', 'Mobile']:
        return 'Tech'
    
    # Cultural, Recreational, and Religious
    elif org_type in ['Culture', 'Religion']:
        return 'Culture'
    
    # Uncategorized and Other Categories
    else:
        return 'Other'
def categorize_income(income):
    if income < 100000:
        return "<$100,000"
    elif income < 200000:
        return "$100,000 - $199,999"
    elif income < 300000:
        return "$200,000 - $299,999"
    elif income < 400000:
        return "$300,000 - $399,999"
    elif income < 500000:
        return "$400,000 - $499,999"
    else:
        return "$500,000+"
       
st.set_page_config(layout='wide')
# Title of the dashboard
st.title("Client Loan Eligibility Prediction Dashboard")
 # Define the columns needed for prediction and additional info
prediction_columns = [
        'SK_ID_CURR', 'DAYS_BIRTH', 'DAYS_ID_PUBLISH', 'REG_CITY_NOT_LIVE_CITY',
        'ORGANIZATION_TYPE', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
        'YEARS_BEGINEXPLUATATION_MODE', 'COMMONAREA_MODE', 'FLOORSMAX_MODE',
        'LIVINGAPARTMENTS_MODE', 'YEARS_BUILD_MEDI', 'CODE_GENDER', 'FLAG_OWN_CAR'
    ]
info_columns = [
        'FLAG_OWN_REALTY', 'AMT_INCOME_TOTAL', 'NAME_INCOME_TYPE',
        'NAME_EDUCATION_TYPE', 'NAME_FAMILY_STATUS', 'NAME_HOUSING_TYPE','AMT_CREDIT'
    ]
    
    # Combine lists of columns to load
columns_to_load = prediction_columns + info_columns

# File uploader allows user to add their own CSV
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, usecols=columns_to_load).dropna()

    # Filter data to include only the relevant columns
    prediction_data = data[prediction_columns]
    info_data = data[info_columns]
    # Filters for selecting a specific entry
    unique_ids = pd.unique(prediction_data['SK_ID_CURR'])
    selected_id = st.sidebar.selectbox('Select Client Number', unique_ids)

    # Display the selected data
    filtered_prediction_data = prediction_data[prediction_data['SK_ID_CURR'] == selected_id]
    filtered_info_data = info_data[prediction_data['SK_ID_CURR'] == selected_id]
    # Use columns to organize layout horizontally
    # Button to make prediction
    # Assuming you have your data prepared in 'filtered_prediction_data'
    if not filtered_prediction_data.empty:
            # Convert the single row DataFrame to a dictionary
            json_data = filtered_prediction_data.iloc[0].to_dict()
            print("Data being sent to API:", json_data)  # Log the data being sent
            
            # Send the data to the API
            response = requests.post('https://mysterious-anchorage-08977-5847c69ff008.herokuapp.com/predict_proba', json=json_data)
            # Display the prediction result
            if response.status_code == 200:
                prediction = response.json()["prediction"] * 100  # Scale to percentage
                st.success(f"Loan Eligibility Score: {prediction:.2f}%")  # Display as percentage
                if prediction >= 80:
                    st.info("This score indicates an excellent likelihood of loan approval. Congratulations, this is a very strong candidate.")
                elif prediction >= 60:
                    st.info("This score indicates a high likelihood of loan approval based on our assessment criteria.")
                elif prediction >= 40:
                    st.info("This score shows a moderate likelihood of loan approval. There may be some conditions or additional verifications needed.")
                elif prediction >= 20:
                    st.info("This score suggests a lower likelihood of loan approval. Consider reviewing the client's details or criteria.")
                else:
                    st.info("This score indicates a very low likelihood of loan approval. It's advisable to assess if the application aligns with the lending criteria.")

                # Create a simple string to download
                csv_string = f"Client number,Prediction Score\n{selected_id},{prediction}"
                st.download_button(
                    label="Download Current Prediction",
                    data=csv_string,
                    file_name='current_prediction.csv',
                    mime='text/csv',
                )
            # Plot the gauge chart without delta
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prediction ,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'shape': "angular",
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#fffef5",
                                 'tickvals': [0, 20, 40, 60, 80, 100], 'ticktext': ["0%", "20%", "40%", "60%", "80%", "100%"] # Specific tick positions
              # Text labels for the ticks
                                },
                        'bgcolor': "#fffef5",
                        'borderwidth': 0,
                        'bordercolor': "rgba(0,0,0,0)",
                        'steps': [
                            {'range': [0, 19.5], 'color': '#f13c0b'},
                            {'range': [19.5, 20.5], 'color': '#fffef5'},
                            {'range': [20.5, 39.5], 'color': '#fe7900'},
                            {'range': [39.5, 40.5], 'color': '#fffef5'},
                            {'range': [40.5, 59.5], 'color': '#ffcf15'},
                            {'range': [59.5, 60.5], 'color': '#fffef5'},
                            {'range': [60.5, 79.5], 'color': '#88c817'},
                            {'range': [79.5, 80.5], 'color': '#fffef5'},
                            {'range': [80.5, 100], 'color': '#01bf11'}
                        ],
                        'threshold': {
                            'line': {'color': "grey", 'width': 4},
                            'thickness': 0.8,
                            'value': prediction 
                        }
                    },
                    number={'valueformat': ".2f", 'suffix': "%"} 
                ))

                # Remove the fill of the gauge
                fig['data'][0]['gauge']['bar']['color'] = "rgba(0,0,0,0)"
            else:
                st.error("Failed to get prediction from server.")
            
    
    import plotly.express as px

    # Assuming `fig` is your Plotly figure created somewhere above this code.
    # ... [Your Plotly figure creation code]

    # Organizing the dashboard
    # Define the column layout

    # Retrieve the necessary data
    client_age = anonymize_birth(filtered_prediction_data['DAYS_BIRTH'].values[0])
    days_since_id_published = categorize_publish_days(filtered_prediction_data['DAYS_ID_PUBLISH'].values[0])
    organization_category = categorize_org_type(filtered_prediction_data['ORGANIZATION_TYPE'].values[0])
    income = categorize_income(filtered_info_data['AMT_INCOME_TOTAL'].values[0])
    
    with st.container(height = 650):
        # Set up the columns for Client Details and Additional Information
        col1, col2, col3 = st.columns([1,2,1])

        with col1:
            st.metric("Client Age", value=client_age)
            st.text("")
            st.metric("Gender", value="Male" if filtered_prediction_data['CODE_GENDER'].values[0] == "M" else "Female")
            st.text("")
            st.metric("Job Field", value=organization_category)
            st.text("")
        with col2:
            # Adjust figure size by specifying the size in update_layout and margins if necessary
            fig.update_layout(
                width=700, 
                height=280, 
                margin=dict(l=20, r=20, t=20, b=10),
                title="Loan Eligibility Probability Gauge",)
            fig.add_annotation(
                    x=0.98,
                    y=0.98,
                    xref='paper',
                    yref='paper',
                    text="?",
                    font=dict(size=24),
                    showarrow=False,
                    hovertext="This gauge represents the predicted probability of the selected client to be eligible  loan",
                    hoverlabel=dict(bgcolor="white", font=dict(size=14))
                )
            st.plotly_chart(fig, use_container_width=True)  # use_container_width is False to respect fig.update_layout size
        with col3:
            st.metric("Income Total", value=income)
            st.text("")
            st.metric("Education Type", value=filtered_info_data['NAME_EDUCATION_TYPE'].values[0].split('/')[0])
            st.text("")
            st.metric("Income Type", value=filtered_info_data['NAME_INCOME_TYPE'].values[0].split('/')[0])
            st.text("")
        col4, col5, col6 , col7= st.columns([1,1,1,1])
        with col4:
            st.metric("Family Status", value=filtered_info_data['NAME_FAMILY_STATUS'].values[0].split('/')[0])
            st.text("")
            st.metric("Housing Type", value=filtered_info_data['NAME_HOUSING_TYPE'].values[0].split('/')[0])
        with col5:
            st.metric("Housing Type", value=filtered_info_data['NAME_HOUSING_TYPE'].values[0].split('/')[0])
            st.text("")
            st.metric("Time Between Receiving ID and Loan Request", value=days_since_id_published)
        with col6:
            st.metric("Owns a Car", value="Yes" if filtered_prediction_data['FLAG_OWN_CAR'].values[0] == "Y" else "No")
            st.text("")
            st.metric("Owns Real Estate", value="Yes" if filtered_info_data['FLAG_OWN_REALTY'].values[0] == "Y" else "No")

        with col7:
            st.metric("Total Credit Amount", value=f"${int(filtered_info_data['AMT_CREDIT'].values[0]):,}")
            st.text("")
            st.metric("Housing Type", value=filtered_info_data['NAME_HOUSING_TYPE'].values[0].split('/')[0])