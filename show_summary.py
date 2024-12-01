import base64
import time
import streamlit as st

from utils import fetch_answer_png, get_image_summary, get_path_summary

def stream_data(input):
    for word in input.split(" "):
        yield word + " "
        time.sleep(0.02)

def generate_summary_button():
    if "fetch_summary" not in st.session_state:
        st.session_state.fetch_summary = False

    if "path_summary" not in st.session_state:
        st.session_state.path_summary = None

    if st.button("Get summary"):
        st.session_state.fetch_summary = True

    if st.session_state.fetch_summary:
        path_summary = ""
        if not st.session_state.path_summary:
            with st.spinner('Generating summary...'):
                st.session_state.make_api_call = False
                node_summary = []
                filters = []

                for node in st.session_state.curr_state.nodes[1:]:
                    response = fetch_answer_png(node)
                    if response:
                        b64_encoded_content = base64.b64encode(response).decode('utf-8')
                        summary = get_image_summary(b64_encoded_content, node.data['filters'])
                        print(f'{node.data["name"]}: {summary}')
                        node_summary.append(summary)
                        filters.append(node.data['filters'])

                path_summary = get_path_summary(node_summary, filters)
                print("----fetched path summary-----")
                print(path_summary)
                print("----fetched path summary 123455-----")
            st.session_state.path_summary = path_summary.replace('$', '\\$')

        if st.session_state.path_summary:
            st.write_stream(stream_data(st.session_state.path_summary))
