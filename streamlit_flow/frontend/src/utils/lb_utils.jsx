const getLbVizListFromLbData = (lbData, vizId) => {
	if (
		lbData &&
		typeof lbData === "object" &&
		lbData.metadata_name &&
		Array.isArray(lbData.contents) &&
		lbData.contents.length > 0
	) {
		var vizIdx = -1;
		lbData.contents.forEach((iterVizData, idx) => {
			if ((iterVizData["visualization_id"] = vizId)) {
				vizIdx = idx;
			}
		});

		if (vizIdx == -1) {
			console.error("viz Id not in lb");
		}

		const vizData = lbData.contents[vizIdx];
		return vizData;
	} else {
		console.error("malformed lb data");
	}

	return null;
};

export default getLbVizListFromLbData;
