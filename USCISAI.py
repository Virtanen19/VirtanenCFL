import os
import streamlit as st
import datetime
from openai import OpenAI
from pdfrw import PdfReader, PdfWriter, PdfDict
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.stateful_button import button


# API KEY
client = OpenAI(api_key="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")


def fill_pdf(template_path, form_details):
    template_pdf = PdfReader(template_path)
    output_pdf = PdfWriter()
    for page in template_pdf.pages:
        if page.Annots:
            for annot in page.Annots:
                if annot.Subtype == '/Widget' and annot.T:
                    field_name = annot.T.to_unicode().strip('()')
                    annot.update(PdfDict(V=form_details[field_name]))
        output_pdf.addpage(page)
    output_path = template_path.replace('.pdf', '_filled.pdf')
    output_pdf.write(output_path)
    return output_path


colored_header(
    label="USCIS AI Form Assistant",
    description="Thank you for using our USCIS application! We are just getting started, so please bare with us as we improve our tool.",
    color_name="red-70", 
)

instructions = {
    "Detailed Instructions": "Enter as detailed of a reason you can for applying to USCIS, some details that may be relevant (but not exclusive) are: Your Citizenship, Your Spouses Citizenship, Marital Status, and Where You Are Currently Living. After you enter your reason for applying, click the 'Get Form Recommendations' button to get a list of recommended forms. After you get the list of recommended forms, you can fill in your details for each form. After this step is completed, please press the 'Click Here When Completed' button to download the filled forms. This button should remain RED, you can then download the individual completed forms.",
    "What Forms Are Supported?": "Being such a new application, we are only able to support forms I-485 and I-130.",
    "Ask Our AI Any Immigration Questions": "Enter your question about USCIS processes below:"
}

# Create a select box in the sidebar
option = st.sidebar.selectbox('Select a Topic or Ask Our AI Any Immigration Questions:', list(instructions.keys()))

# Conditional display based on selected option
if option == "Ask Our AI Any Immigration Questions":
    user_query = st.sidebar.text_input("Ask any question about USCIS processes:")
    if st.sidebar.button("Submit Question"):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant skilled in US immigration processes."},
                {"role": "user", "content": user_query}
            ]
        )
        answer = response.choices[0].message.content
        st.sidebar.write(answer)
else:
    st.sidebar.write(instructions[option])

st.write('This tool helps determine which USCIS forms you may need to fill out based on your specific situation.')

if 'form_details' not in st.session_state:
    st.session_state.form_details = {}

reason_for_applying = st.text_area('Why are you applying to USCIS? Describe your situation:', height=150)
if st.button('Get Form Recommendations'):
    st.session_state['reason_for_applying'] = reason_for_applying
    completion_response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are an assistant skilled in US immigration processes."},
            {"role": "user", "content": st.session_state['reason_for_applying']}
        ]
    )
    st.session_state['form_recommendations'] = completion_response.choices[0].message.content
    st.session_state['form_fields'] = {}

if 'form_recommendations' in st.session_state:
    st.subheader('Recommended USCIS Forms:')
    st.write(st.session_state['form_recommendations'])

    with stylable_container(

        key="red_button",

        css_styles="""

            button {

                background-color: red;

                color: white;

                border-radius: 20px;

            }

            """,

    ):

        st.button("Reminder: Currently, this tool only supports forms I-485 and I-130. Although we cannot help you complete any other forms, please take all our recommendations into consideration.")



  
    # Define minimum and maximum dates
    min_date = datetime.date(1900, 1, 1)
    max_date = datetime.date(2050, 12, 31)
    
    state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}
    form_fields = {
        'I-485': [('First name', 'Enter your first name:', ' '), 
                  ('Last Name', 'Enter your last name:', ' '), 
                  ('Middle Name', 'Enter your middle name:', ' '),
                  ('Volag Number', 'Enter your Volag Number: ', 'Only to be completed by an attorney or accredited representative (if any).'), 
                  ('USCIS Online Account Number', 'Enter your USCIS online account number:', ' '),
                  ('Male', 'Enter an X only if you are a Male', 'Enter an X only if this is your Sex'),
                  ('Female', 'Enter an X only if you are a Female','Enter an X only if this is your Sex'), 
                  ('DOB', 'Enter your date of birth:', 'date')],
        'I-130': [('First Name', 'Enter your first name:', ' '), 
                  ('Last Name', 'Enter your last name:', ' '),
                  ('Middle Name', 'Enter your middle name:', ' '),
                  ('Volag Number', 'Enter your Volag Number: ', 'Only to be completed by an attorney or accredited representative (if any).'), 
                  ('USCIS Online Account Number', 'If your are the attorney or Accredited Representative of Petitioner, enter your USCIS online account number:', 'Only to be completed by an attorney or accredited representative (if any).'),
                  ('USCIS Online Account Number 2', 'Enter your USCIS online account number:', ' '),
                  ('SpouseCheckBox', 'Enter an X only if your relationship to the benficiary is: Spouse', 'Enter an X only if this represents who your are filing for'),
                  ('ParentCheckBox', 'Enter an X only if your relationship to the benficiary is: Parent', 'Enter an X only if this represents who your are filing for'),
                  ('Brother-SisterCheckBox', 'Enter an X only if your relationship to the benficiary is: Brother/Sister', 'Enter an X only if this represents who your are filing for'),
                  ('ChildCheckBox', 'Enter an X only if your relationship to the benficiary is: Child', 'Enter an X only if this represents who your are filing for'),  
                  ('Alien Registration Number', 'Enter your Alien Registration Number (A-Number):', ' '), 
                  ('Street Number', 'What is your street number and name:', ' '), 
                  ('City', 'Enter your city:', ' '), 
                  ('State', 'Select your state:', ' '), 
                  ('ZipCode', 'Enter your zip code:', ' '),
                  ('Province', '(If outside of the United States) Enter the province name:','Enter only if you live outside of the United States'),  
                  ('Postal Code', '(If outside of the United States) Enter the postal code:','Enter only if you live outside of the United States'), 
                  ('Country', 'Enter your country:', ' '), 
                  ('In Care Of', 'Enter the name of the person that the mail should be sent to:', ' ')]
    }
   
   

    for form, fields in form_fields.items():
            if form in st.session_state['form_recommendations']:
                with st.expander(f"Fill in your details for {form}"):
                    for field_name, prompt, *options in fields:
                        key = f"{form}_{field_name.replace(' ', '_').lower()}"
                        if field_name == 'State':
                    # Use a select box for State field with abbreviations
                            selected_state = st.selectbox(prompt, list(state_abbreviations.values()), key=key)
                            st.session_state.form_fields[key] = selected_state
                        elif options and options[0] == 'date':
                            date_input = st.date_input(
                                prompt, 
                                min_value=min_date, 
                                max_value=max_date, 
                                key=key
                            )
                            if date_input:
                                formatted_date = date_input.strftime('%m/%d/%Y')
                                st.session_state.form_fields[key] = formatted_date
                            else:
                                st.session_state.form_fields[key] = ''
                        else:
                            placeholder = options[0] if options else ''
                            st.session_state.form_fields[key] = st.text_input(prompt, value='', placeholder=placeholder, key=key)


    if button('Click Here When Completed, Button Will Turn Red When You Can Download Forms', key='download_forms'):
        for form, fields in form_fields.items():
            if form in st.session_state['form_recommendations']:
                form_details = {field_name: st.session_state.form_fields[f"{form}_{field_name.replace(' ', '_').lower()}"] for field_name, _, *options in fields}
                output_path = fill_pdf(f'{form}(Modified).pdf', form_details)
                with open(output_path, "rb") as file:
                    st.download_button(f'Download Filled USCIS Form {form}', file.read(), f'USCIS_Form_{form}_filled.pdf')
