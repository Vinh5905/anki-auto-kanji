from support_func import add_notes, check_potential_add_notes, save_to_csv

def kanji_data_review(st, ss_state, type='dataframe'):
    column_config = {
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

    match type:
        case 'dataframe':
            return st.dataframe(
                st.session_state[ss_state],
                use_container_width=True,  
                column_config=column_config
            )
        case 'data_editor':
            return st.data_editor(
                st.session_state[ss_state],
                use_container_width=True,  
                column_config=column_config
            )
        case '_':
            raise ValueError('Kanji data review not in (dataframe, data_editor)')

def save(st, df_name, edited_df_data, num):
    key_save = f'click_save_{num}'
    ss_save = f'save_{num}'
    result = f'result_{num}'

    if ss_save not in st.session_state:
        st.session_state[ss_save] = False

    save = st.button(label='Save', type='primary', key=key_save)
    if save or st.session_state[ss_save]:
        st.session_state[ss_save] = True

        with st.spinner('Saving...'):
            st.divider()
            st.subheader(":rainbow[Status of cards when add to Anki]")

            if st.session_state[key_save]:
                st.session_state[df_name] = edited_df_data

                data_dict = st.session_state[df_name].to_dict('records')

                canAdd = check_potential_add_notes(data_dict)

                save_to_csv(data_dict)
                response = add_notes(data_dict, canAdd)

                st.toast('Save successfully', icon='🎉')

                result_add = st.session_state[df_name].copy()
                result_add['Add Status'] = canAdd
                
                st.session_state[result] = result_add

            if result in st.session_state:
                data_result = kanji_data_review(st, result)
                st.write(':orange[__Lưu ý:__] _Nếu từ ở trạng thái không tích nghĩa là :green[__đã tồn tại__] từ đó trong Anki của bạn !!_')