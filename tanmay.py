# example.py
import os
import random
import base64
from uuid import uuid4

import requests
import streamlit as st
from dotenv import load_dotenv

from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
from streamlit_flow.layouts import TreeLayout
from streamlit_flow.state import StreamlitFlowState
from utils import fetch_answer_png, get_image_summary, get_path_summary, merge_filters

# Load .env file
load_dotenv("./streamlit_flow/frontend/.env.local")
lb_api_url = os.getenv("LB_FETCH_API_URL")
bearer_token = os.getenv("BEARER_TOKEN")
lb_id = os.getenv("LIVEBOARD_ID")
answer_fetch_url = os.getenv("ANSWER_FETCH_API_URL")
openai_api_key = os.getenv("OPEN_AI_API_KEY")

st.set_page_config("Myth demo", layout="wide")
st.title("MYTh demo")

if "lb_data" not in st.session_state:
    try:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }

        req_data = {
            "metadata_identifier": lb_id,
            "data_format": "FULL",
            "record_offset": 0,
            "record_size": 100,
        }

        response = requests.post(lb_api_url, headers=headers, json=req_data)

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
    except Exception as e:
        st.session_state.api_error = f"An error occurred: {e}"
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
            "1", (0, 0), {"content": "Image Fetch Node", "name": "testing"}, "imageFetch", "right", "left"
        ),  # <-- Custom Node
    ]
    edges = []
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)

# ------ Show the all the inputs for add node -----------
visualization_map = {
    item['visualization_name']: item['visualization_id'] for item in st.session_state.lb_data['contents']
}
visualization_ids = [item["visualization_id"] for item in st.session_state.lb_data['contents']]

# Create a dropdown selectbox with the visualization names
visualization_map = {item["visualization_name"]: item["visualization_id"] for item in st.session_state.lb_data['contents']}

# Select a visualization using its name
selected_visualization_name = st.selectbox("Select a visualization", options=list(visualization_map.keys()))

# Get the selected data based on the selected visualization name
selected_data = next((item for item in st.session_state.lb_data['contents'] if item["visualization_id"] == visualization_map[selected_visualization_name]), None)

# Extract 'name' from each node's data
node_names = [node.data["name"] for node in st.session_state.curr_state.nodes]

# Add a "None" or similar option for no selection
options = ["None"] + node_names
selected_parent = st.selectbox("Select a parent node:", options=options, index=0)

# Provide feedback to the user about their selection
st.write("Add filter!")

#  Assuming you have a function to extract unique values for a given column
def get_unique_values(content, column_name):
    # Simulates extracting unique values for a column from the given content data rows
    return list(set(row[column_name] for row in content.get('data_rows', [])))

filters = {}
if selected_data:
    # Extract column names for the selected visualization
    column_names = selected_data["column_names"]
    
    # Display checkboxes for each column name and track selections
    for column in column_names:
        if st.checkbox(column, key=f"{selected_visualization_name}_{column}"):
            unique_values = get_unique_values(selected_data, column)
            filters[column] = unique_values

if st.button("Add Node"):
    print("Adding node!")
    new_node_id = str(f"st-flow-node_{uuid4()}")
    if selected_parent != "None":
        # Find the parent node
        parent_node = next((node for node in st.session_state.curr_state.nodes if node.data['name'] == selected_parent), None)
        if parent_node:
            # Extract filters from the parent node
            parent_filters = parent_node.data.get('filters', {})
            
            # Merge parent filters with any existing filters
            filters = merge_filters(parent_filters, filters)

        new_edge = StreamlitFlowEdge(
            f'{parent_node.id}->{new_node_id}',
            parent_node.id,
            new_node_id,
            animated=True,
            marker_start={},
            marker_end={"type": "arrow"},
        )
        st.session_state.curr_state.edges.append(new_edge)

    new_node = StreamlitFlowNode(
        new_node_id,
        (random.uniform(-100, 100), random.uniform(-100, 100)),
        {"content": f"Node {len(st.session_state.curr_state.nodes) + 1}", "vizId": visualization_map[selected_visualization_name], "lbId": lb_id, "filters": filters, "name": selected_visualization_name},
        "answer",
        "right",
        "left",
    )
    st.session_state.curr_state.nodes.append(new_node)
    st.rerun()


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

print(st.session_state.curr_state.nodes)


if "node_summary" not in st.session_state:
    st.session_state.node_summary = []

for idx, summary in enumerate(st.session_state.node_summary):
    st.write(f"Summary for {st.session_state.curr_state.nodes[idx + 1].data['name']}: {summary}")


if st.button("Get summary"):
    # Iterate through nodes and make API calls
    api_responses = []
    node_summary = []
    filters = []
    
    for node in st.session_state.curr_state.nodes[1:]:
        response = fetch_answer_png(node, bearer_token, answer_fetch_url)
        if response:
            api_responses.append(response)
            b64_encoded_content = base64.b64encode(response).decode('utf-8')
            summary = get_image_summary(b64_encoded_content, node.data['filters'], openai_api_key)
            print(f'{node.data["name"]}: {summary}')
            node_summary.append(summary)
            filters.append(node.data['filters'])

    print(node_summary)

    path_summary = get_path_summary(node_summary, filters, openai_api_key)
    print("----path summary-----")
    print(path_summary)

    st.session_state.node_summary = node_summary  # Store node summaries

    # filename = "analysis_summary.txt"  # Specify your desired filename
    # with open(filename, "w") as file:
    #     for summary in node_summary:
    #         file.
    #     file.write(path_summary)

    # Confirmation message
    # print(f"Summary written to {filename}.")

    # Optionally, you can add a message to indicate summaries have been fetched
    st.success("Summaries fetched successfully!")
