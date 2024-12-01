import os
import random
from uuid import uuid4
from dotenv import load_dotenv
import streamlit as st

from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
from utils import merge_filters

load_dotenv("./streamlit_flow/frontend/.env.local")
lb_id = os.getenv("LIVEBOARD_ID")

def find_most_changed_attributes():
    visualization_map = {
        item["visualization_name"]: item["visualization_id"] 
        for item in st.session_state.lb_data['contents'] 
        if item["visualization_name"][:3] != "CCA"
    }
    # Extract 'name' from each node's data
    node_names = [node.data["name"] for node in st.session_state.curr_state.nodes[1:] if node.data["name"][:4] != "CCA:"]

    # Add a "None" or similar option for no selection
    options = ["None"] + node_names
    selected_kpi = st.selectbox("Select KPI to find its most changing attributes", options=options, index=0, key="cca")

    if selected_kpi != "None":
        if st.button("Add CCA Node"):
            filters = {}
            # Find the parent node
            parent_node = next((node for node in st.session_state.curr_state.nodes if node.data['name'] == selected_kpi), None)
            if parent_node:
                # Extract filters from the parent node
                parent_filters = parent_node.data.get('filters', {})

                # Merge parent filters with any existing filters
                filters = merge_filters(parent_filters, filters)

            for viz in st.session_state.lb_data['contents']:
                new_node_id = str(f"st-flow-node_{uuid4()}")
                if viz['visualization_name'].startswith("CCA: " + selected_kpi):
                    new_node = StreamlitFlowNode(
                        new_node_id,
                        (random.uniform(-100, 100), random.uniform(-100, 100)),
                        {"content": f"Node {len(st.session_state.curr_state.nodes) + 1}", "vizId": viz['visualization_id'], "lbId": lb_id, "filters": filters, "name": viz['visualization_name']},
                        "answer",
                        "right",
                        "left",
                    )
                    st.session_state.curr_state.nodes.append(new_node)

                    new_edge = StreamlitFlowEdge(
                        f'{parent_node.id}->{new_node_id}',
                        parent_node.id,
                        new_node_id,
                        animated=True,
                        marker_start={},
                        marker_end={"type": "arrow"},
                    )
                    st.session_state.curr_state.edges.append(new_edge)
            st.rerun()
