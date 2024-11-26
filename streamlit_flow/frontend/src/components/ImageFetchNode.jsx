// components/ImageFetchNode.jsx
import {
	LiveboardEmbed,
	useEmbedRef,
} from "@thoughtspot/visual-embed-sdk/react";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Handle } from "reactflow";
import { withStreamlitConnection } from "streamlit-component-lib";
import getLbVizListFromLbData from "../utils/lb_utils";

const FETCH_IMAGE_API_URL = process.env.REACT_APP_FETCH_IMAGE_API_URL;
const FETCH_FILTER_API_URL = process.env.REACT_APP_FETCH_FILTER_API_URL;
const BEARER_TOKEN = process.env.REACT_APP_BEARER_TOKEN;

// Define the mapping for secondary dropdowns based on filter names
const filterOptionsMap = {
	ATTRIBUTE_COL: ["IN", "NOT IN"],
	MEASURE_COL: ["GT", "LT", "EQ"],
	// Add more mappings as needed
};

const ImageFetchNode = ({ args }) => {
	console.log(args);
	// const vizId = args.nodes[args.nodes.length - 1].data['vizId'];
	const lbData = args.lbData;
	const vizId = "43676666-794f-42d7-aa74-586dea6b69d9";
	const [inputId, setInputId] = useState("");
	const [metadataName, setMetadataName] = useState(""); // For node heading
	const [filters, setFilters] = useState([]); // Array of filter objects { name: string, values: array }
	const [selectedFilters, setSelectedFilters] = useState({}); // { filterName: selectedValue }
	const [filterEnabled, setFilterEnabled] = useState({}); // { filterName: boolean }
	const [filterListSelections, setFilterListSelections] = useState({}); // { filterName: selectedList }
	const [loadingFilters, setLoadingFilters] = useState(false);
	const [error, setError] = useState(null);

	const embedRef = useEmbedRef();

	const handleFilterChange = (filterName, selectedValue) => {
		const updatedFilters = {
			...selectedFilters,
			[filterName]: selectedValue,
		};
		setSelectedFilters(updatedFilters);
	};

	const handleFilterEnableChange = (filterName, isEnabled) => {
		const updatedEnabled = {
			...filterEnabled,
			[filterName]: isEnabled,
		};
		setFilterEnabled(updatedEnabled);
	};

	const handleFilterListChange = (filterName, selectedList) => {
		const updatedListSelections = {
			...filterListSelections,
			[filterName]: selectedList,
		};
		setFilterListSelections(updatedListSelections);
	};

	const handleVizFilters = async () => {
		setLoadingFilters(true);
		setError(null);
		setMetadataName(""); // Reset previous metadata name
		setFilters([]); // Reset previous filters
		setSelectedFilters({}); // Reset previous selections
		setFilterEnabled({}); // Reset filter enabled states

		try {
			const vizData = getLbVizListFromLbData(lbData, vizId);
			setMetadataName(vizData.visualization_name);
			const columnNames = vizData.column_names;
			const dataRows = vizData.data_rows;

			// Extract unique values for each column
			const extractedFilters = columnNames.map((col) => {
				const uniqueValues = Array.from(
					new Set(
						dataRows
							.map((row) => row[col])
							.filter((val) => val !== undefined && val !== null)
					)
				);
				return {
					name: col,
					values: uniqueValues,
				};
			});

			setFilters(extractedFilters);

			// Initialize selectedFilters with the first value of each filter
			const initialSelected = {};
			extractedFilters.forEach((filter) => {
				initialSelected[filter.name] = filter.values[0] || "";
			});
			setSelectedFilters(initialSelected);
		} catch (err) {
			console.error(err);
			setError("Failed to fetch filters. Please try again.");
		} finally {
			setLoadingFilters(false);
		}
	};

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
			{metadataName && (
				<div
					style={{
						marginTop: "10px",
						fontWeight: "bold",
						fontSize: "16px",
					}}
				>
					{metadataName}
				</div>
			)}

			<div>
				<input
					type="text"
					placeholder="Enter Answer ID"
					value={inputId}
					onChange={(e) => setInputId(e.target.value)}
					style={{
						width: "100%",
						padding: "5px",
						marginBottom: "5px",
						boxSizing: "border-box",
					}}
				/>
				<button
					onClick={handleVizFilters}
					disabled={loadingFilters}
					style={{ width: "100%", padding: "5px", cursor: "pointer" }}
				>
					{loadingFilters ? "Fetching..." : "Fetch Chart & Filters"}
				</button>
				{error && (
					<div style={{ color: "red", marginTop: "5px" }}>
						{error}
					</div>
				)}
				{inputId && (
					<div className="lb-embed-container">
						<LiveboardEmbed
							ref={embedRef}
							dataPanelV2={false}
							additionalFlags={{
								overrideConsoleLogs: false,
							}}
							liveboardId={inputId}
							vizId={vizId}
							hideSearchBar={true}
							hideDataSources={true}
							frameParams={{
								height: "100%",
								weight: "100%",
							}}
							className="lb-embed-body"
						/>
					</div>
				)}
				{filters.length > 0 && (
					<div style={{ marginTop: "10px" }}>
						{filters.map((filter, index) => (
							<div
								key={index}
								style={{
									display: "flex",
									alignItems: "center",
									marginBottom: "10px",
								}}
							>
								{/* Checkbox for enabling/disabling the filter */}
								<input
									type="checkbox"
									checked={
										filterEnabled[filter.name] || false
									}
									onChange={(e) =>
										handleFilterEnableChange(
											filter.name,
											e.target.checked
										)
									}
									style={{ marginRight: "10px" }}
								/>
								{/* Filter Name */}
								<label
									style={{
										marginRight: "10px",
										minWidth: "100px",
									}}
								>
									{filter.name}
								</label>
								{/* Primary Dropdown for filter values */}
								<select
									value={selectedFilters[filter.name] || ""}
									onChange={(e) =>
										handleFilterChange(
											filter.name,
											e.target.value
										)
									}
									disabled={!filterEnabled[filter.name]}
									style={{
										padding: "5px",
										marginRight: "10px",
										flex: 1,
									}}
								>
									{filter.values.map((value, idx) => (
										<option key={idx} value={value}>
											{value}
										</option>
									))}
								</select>
								{/* Secondary Dropdown based on the mapping */}
								<select
									value={
										filterListSelections[filter.name] || ""
									}
									onChange={(e) =>
										handleFilterListChange(
											filter.name,
											e.target.value
										)
									}
									disabled={!filterEnabled[filter.name]}
									style={{
										padding: "5px",
										flex: 1,
									}}
								>
									{/* Populate options from the filterOptionsMap */}
									{filterOptionsMap["ATTRIBUTE_COL"] ? (
										filterOptionsMap["ATTRIBUTE_COL"].map(
											(option, idx) => (
												<option
													key={idx}
													value={option}
												>
													{option}
												</option>
											)
										)
									) : (
										<option value="">No Options</option>
									)}
								</select>
							</div>
						))}
					</div>
				)}
			</div>
			<Handle type="source" position="bottom" />
		</div>
	);
};

ImageFetchNode.propTypes = {
	id: PropTypes.string.isRequired,
	data: PropTypes.object.isRequired,
};

export default withStreamlitConnection(ImageFetchNode);
