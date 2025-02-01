import streamlit as st
from support_func import get_list_item_from_response, transform_list_to_dict, response_from_gpt, save_to_csv, add_notes, check_potential_add_notes, read_data_from_csv, disable_app_napp
from st_support_func import kanji_data_review, save
import pandas as pd
import csv

st.set_page_config(layout='wide')

if 'app-napp-disabled' not in st.session_state:
    st.session_state['app-napp-disabled'] = True
    disable_app_napp(st.session_state['app-napp-disabled'])

st.title('Welcome back, :rainbow[Kevin Pham]! :sunglasses:')
st.divider()

st.markdown('''
    <style>
    /* Thay đổi khoảng cách giữa các tab */
    div.stTabs > div > div > div {
        gap: 3rem !important;
    }
            
    button[data-baseweb='tab'] p {
        font-size: 18px;
        font-weight: 600;
    }
    </style>
''', unsafe_allow_html=True)

st.subheader(':rainbow[Choose way to add?]')
all_tabs = st.tabs(["LIST KANJI", "CSV", "EXCEL"])

# WAY OF LIST KANJI
with all_tabs[0]:
    st.subheader(":rainbow[What kanji you want to add to Anki today?]")
    # text area
    placeholder = '''What kanji N3 you want to add to Anki today?
    Example: 
        教室
        大学
        代表
    '''

    kanji_list = st.text_area(
        label='Kanji you want to add ~~', 
        placeholder=placeholder,
        height=300,
        label_visibility='collapsed'
    )

    if 'translate' not in st.session_state:
        st.session_state['translate'] = False

    translate = st.button(label='Translate', type='primary')
    if translate or st.session_state['translate']:
        st.session_state['translate'] = True

        with st.spinner('Translating...'):
            if 'df_list_kanji' not in st.session_state:
                # data from gpt to anki
                st.snow()
                kanji_list = kanji_list.split('\n')
                kanji_list = [item.strip() for item in kanji_list if item]
                kanji_not_dup = []
                for kanji in kanji_list:
                    if kanji not in kanji_not_dup:
                        kanji_not_dup.append(kanji)

                data_response = response_from_gpt(kanji_not_dup)
                st.toast('Get data from GPT successfully', icon='🎉')
                data_list = get_list_item_from_response(data_response)
                data_dict = transform_list_to_dict(data_list)

                # data from csv to anki
                # data_csv = read_data_from_csv()
                # data_dict = transform_list_to_dict(data_csv)

                df = pd.DataFrame(data_dict)
                st.session_state['df_list_kanji'] = df

            st.divider()
            st.subheader(":rainbow[Review before save]")

            edited_df_list_kanji = kanji_data_review(st, 'df_list_kanji', 'data_editor')
            save(st, 'df_list_kanji', edited_df_list_kanji, 0)


# WAY OF CSV
with all_tabs[1]:
    uploaded_file = st.file_uploader('Choose a CSV file!')
    if uploaded_file is not None:
        with st.spinner('Loading...'):
            if 'df_csv' not in st.session_state:
                # Đọc file CSV
                data_csv = csv.DictReader(uploaded_file.read().decode('utf-8').splitlines())
                # Hiển thị từng hàng trong file CSV
                rows = []
                for row in data_csv:
                    rows.append(row)

                df = pd.DataFrame(rows)
                st.session_state['df_csv'] = df

            # ĐOẠN COPY
            st.divider()
            st.subheader(":rainbow[Review before save]")

            edited_df_csv = kanji_data_review(st, 'df_csv', 'data_editor')
            save(st, 'df_csv', edited_df_csv, 1)


# WAY OF EXCEL
with all_tabs[2]:
    uploaded_file = st.file_uploader('Choose a EXCEL file!', type=['xlsx', 'xls'])
    if uploaded_file is not None:
        with st.spinner('Loading...'):
            if 'df_excel' not in st.session_state:
                data_excel = pd.read_excel(uploaded_file, engine='openpyxl') # dataframe
                data_excel_to_dict = data_excel.to_dict('records')

                st.session_state['df_excel'] = data_excel

            # ĐOẠN COPY
            st.divider()
            st.subheader(":rainbow[Review before save]")

            edited_df_excel = kanji_data_review(st, 'df_excel', 'data_editor')
            save(st, 'df_excel', edited_df_excel, 2)
