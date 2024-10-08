import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout, RadialLayout

st.set_page_config("Streamlit Flow Example", layout="wide")

st.title("Streamlit Flow Example")


if 'curr_state' not in st.session_state:
	nodes = [StreamlitFlowNode("1", (0, 0), {'content': 'Node 1'}, 'input', 'right'),
			StreamlitFlowNode("2", (1, 0), {'content': 'Node 2'}, 'default', 'right', 'left'),
			StreamlitFlowNode("3", (2, 0), {'content': 'Node 3'}, 'default', 'right', 'left'),
			# StreamlitFlowNode("4", (2, 1), {'content': 'Node 4'}, 'output', target_position='left'),
			# StreamlitFlowNode("5", (3, 0), {'content': 'Node 5'}, 'output', target_position='left'),
			# StreamlitFlowNode("6", (3, 1), {'content': 'Node 6'}, 'output', target_position='left'),
			# StreamlitFlowNode("7", (4, 0), {'content': 'Node 7'}, 'output', target_position='left'),
			]

	edges = [StreamlitFlowEdge("1-2", "1", "2", animated=True),
			StreamlitFlowEdge("1-3", "1", "3", animated=True),
			# StreamlitFlowEdge("2-4", "2", "4", animated=True),
			# StreamlitFlowEdge("2-5", "2", "5", animated=True),
			# StreamlitFlowEdge("3-6", "3", "6", animated=True),
			# StreamlitFlowEdge("3-7", "3", "7", animated=True)
			]
	
	st.session_state.curr_state = StreamlitFlowState(nodes, edges)


if st.button("Add node"):
	new_node = StreamlitFlowNode(str(len(st.session_state.curr_state.nodes) + 1), (0, 0), {'content': f'Node {len(st.session_state.curr_state.nodes) + 1}'}, 'default', 'right', 'left')
	st.session_state.curr_state.nodes.append(new_node)
	st.rerun()

st.session_state.curr_state = streamlit_flow('example_flow', 
								st.session_state.curr_state, 
								layout=TreeLayout(direction='right'), 
								fit_view=True, 
								height=500, 
								enable_node_menu=True,
								enable_edge_menu=True,
								enable_pane_menu=True,
								get_edge_on_click=True,
								get_node_on_click=True, 
								show_minimap=True, 
								hide_watermark=True, 
								allow_new_edges=True,
								min_zoom=0.1)

col1, col2, col3 = st.columns(3)

with col1:
	for node in st.session_state.curr_state.nodes:
		st.write(node)

with col2:
	for edge in st.session_state.curr_state.edges:
		st.write(edge)

with col3:
	st.write(st.session_state.curr_state.selected_id)