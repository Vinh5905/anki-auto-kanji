import streamlit as st
from main import get_list_item_from_response, transform_list_to_dict, response_from_gpt, save_to_csv, add_notes, check_potential_add_notes, read_data_from_csv, disable_app_napp
import pandas as pd

st.set_page_config(layout='wide')

if 'app-napp-disabled' not in st.session_state:
    st.session_state['app-napp-disabled'] = True
    disable_app_napp(st.session_state['app-napp-disabled'])

st.title('Welcome back, :rainbow[Kevin Pham]! :sunglasses:')
st.divider()

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

if 'save' not in st.session_state:
    st.session_state['save'] = False

translate = st.button(label='Translate', type='primary')
if translate or st.session_state['translate']:
    st.session_state['translate'] = True
    with st.spinner('Translating...'):
        if 'df' not in st.session_state:
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
            st.session_state['df'] = df

        st.session_state['translate'] = True

        st.divider()
        st.subheader(":rainbow[Review before save]")

        edited_df = st.data_editor(
            st.session_state['df'],
            use_container_width=True,  
            column_config={
                "Kanji": st.column_config.Column(
                    width="medium",
                    required=True,
                ),
                "Hiragana": st.column_config.Column(
                    width="large",
                    required=True,
                ),
                "Chinese character": st.column_config.Column(
                    width="medium",
                    required=True,
                ),
                "Meaning": st.column_config.Column(
                    width="large",
                    required=True,
                )
            }
        )

    save = st.button(label='Save', type='primary', key='save_clicked')
    if save or st.session_state['save']:
        st.session_state['save'] = True

        with st.spinner('Saving...'):
            st.divider()
            st.subheader(":rainbow[Status of cards when add to Anki]")

            if st.session_state['save_clicked']:
                st.session_state['df'] = edited_df

                data_dict = st.session_state['df'].to_dict('records')

                canAdd = check_potential_add_notes(data_dict)

                save_to_csv(data_dict)
                ressponse = add_notes(data_dict, canAdd)
                print(ressponse)

                st.toast('Save successfully', icon='🎉')

                result_add = st.session_state['df'].copy()
                result_add['Add Status'] = canAdd

                st.session_state['result'] = result_add

            if 'result' in st.session_state:
                st.dataframe(
                    st.session_state['result'],
                    use_container_width=True,  
                    column_config={
                        "Kanji": st.column_config.Column(
                            width="medium",
                            required=True,
                        ),
                        "Hiragana": st.column_config.Column(
                            width="large",
                            required=True,
                        ),
                        "Chinese character": st.column_config.Column(
                            width="medium",
                            required=True,
                        ),
                        "Meaning": st.column_config.Column(
                            width="large",
                            required=True,
                        ),
                        "Add Status": st.column_config.Column(
                            width="medium",
                            required=True,
                        )
                    }
                )

                st.write(':orange[__Lưu ý:__] _Nếu từ ở trạng thái không tích nghĩa là :green[__đã tồn tại__] từ đó trong Anki của bạn !!_')
        