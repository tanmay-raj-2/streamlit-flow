import streamlit as st

from add_cca import find_most_changed_attributes
from add_node import add_node_button
from show_summary import generate_summary_button
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode
from streamlit_flow.layouts import TreeLayout
from streamlit_flow.state import StreamlitFlowState
from utils import get_lb_data

st.set_page_config("Myth demo", layout="wide")
st.title("MYTh demo")

if "lb_data" not in st.session_state:
    response = get_lb_data()
        # Check if the request was successful
    if response.status_code == 200:
        # Assuming the API returns JSON data
        st.session_state.lb_data = response.json()
        st.session_state.api_error = None
    else:
        st.session_state.api_error = (
            f"API request failed with status code {response.status_code}."
        )
        st.session_state.lb_data = None


# Display the fetched data or error message
if st.session_state.api_error:
    st.error(st.session_state.api_error)

if st.session_state.lb_data:
    st.subheader(f"Liveboard - {st.session_state.lb_data['metadata_name']}")
    st.json(st.session_state.lb_data)

if "curr_state" not in st.session_state:
    nodes = [
        StreamlitFlowNode(
            "1", (0, 0), {"content": "Image Fetch Node", "name": "testing"}, "imageFetch", "right", "left", hidden=True
        ),  # <-- Custom Node
    ]
    edges = []
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)

# ------ Logic to add nodes -----------
add_node_button()

print('--' * 20)
print(st.session_state.curr_state.nodes)
print('--' * 20)

# ------ Logic to get the most changing attributes -----------
find_most_changed_attributes()


# Render the Flowchart
st.session_state.curr_state = streamlit_flow(
    "example_flow",
    st.session_state.curr_state,
    layout=TreeLayout(direction="right"),
    fit_view=True,
    height="75rem",
    enable_node_menu=True,
    enable_edge_menu=True,
    enable_pane_menu=True,
    get_edge_on_click=True,
    get_node_on_click=True,
    show_minimap=True,
    hide_watermark=True,
    allow_new_edges=True,
    animate_new_edges=True,
    min_zoom=0.1,
    lb_data=st.session_state.lb_data,
)

# ------ Logic to generate the AI Summary -----------
generate_summary_button()
