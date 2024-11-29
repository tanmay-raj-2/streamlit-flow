import os
import random
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st

from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
from utils import merge_filters

load_dotenv("./streamlit_flow/frontend/.env.local")
lb_id = os.getenv("LIVEBOARD_ID")

def add_node_button():
    visualization_map = {
        item['visualization_name']: item['visualization_id'] for item in st.session_state.lb_data['contents']
    }
    visualization_ids = [item["visualization_id"] for item in st.session_state.lb_data['contents']]

    # Create a dropdown selectbox with the visualization names
    visualization_map = {item["visualization_name"]: item["visualization_id"] for item in st.session_state.lb_data['contents']}

    # Select a visualization using its name
    selected_visualization_name = st.selectbox("Select a visualization", options=list(visualization_map.keys()))


    # Extract 'name' from each node's data
    node_names = [node.data["name"] for node in st.session_state.curr_state.nodes]

    # Add a "None" or similar option for no selection
    options = ["None"] + node_names
    selected_parent = st.selectbox("Select a parent node:", options=options, index=0)

    filters = {}

    if selected_parent != "None":
        # Get the selected data based on the selected visualization name
        selected_data = next((item for item in st.session_state.lb_data['contents'] if item["visualization_id"] == visualization_map[selected_parent]), None)

        # Provide feedback to the user about their selection
        st.write("Add filter!")

        #  Assuming you have a function to extract unique values for a given column
        def get_unique_values(content, column_name):
            # Simulates extracting unique values for a column from the given content data rows
            return list(set(row[column_name] for row in content.get('data_rows', [])))

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
