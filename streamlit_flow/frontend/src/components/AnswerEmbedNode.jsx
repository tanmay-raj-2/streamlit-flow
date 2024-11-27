// components/AnswerEmbedNode.jsx
import {
	LiveboardEmbed,
	RuntimeFilterOp,
	useEmbedRef,
} from "@thoughtspot/visual-embed-sdk/react";
import PropTypes from "prop-types";
import React from "react";
import { Handle } from "reactflow";

const AnswerEmbedNode = ({ data }) => {
	const lbId = data.lbId;
	const vizId = data.vizId;
	const filters = data.filters;

	const runTimeFileters = Object.entries(filters).map(
		([columnName, values]) => ({
			columnName: columnName,
			operator: RuntimeFilterOp.IN,
			values: values,
		})
	);

	const embedRef = useEmbedRef();
	return (
		<div
			className="image-fetch-node"
			style={{
				padding: "10px",
				border: "1px solid #ddd",
				borderRadius: "5px",
				background: "#fff",
			}}
		>
			<Handle type="target" position="top" />
			<div className="lb-embed-container">
				<LiveboardEmbed
					ref={embedRef}
					dataPanelV2={false}
					additionalFlags={{
						overrideConsoleLogs: false,
					}}
					liveboardId={lbId}
					vizId={vizId}
					hideSearchBar={true}
					hideDataSources={true}
					frameParams={{
						height: "100%",
						weight: "100%",
					}}
					className="lb-embed-body"
					runtimeFilters={runTimeFileters}
					customizations={{
						style: {
							customCSS: {
								rules_UNSTABLE: {
									".embed-module__tsEmbedContainer": {
										overflow: "initial !important",
									},
								},
							},
						},
					}}
				/>
			</div>
			<Handle type="source" position="bottom" />
		</div>
	);
};

AnswerEmbedNode.propTypes = {
	id: PropTypes.string.isRequired,
	data: PropTypes.object.isRequired,
};

export default AnswerEmbedNode;
