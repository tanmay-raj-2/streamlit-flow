import "@xyflow/react/dist/style.css";
import React from "react";
import { createRoot } from "react-dom/client";
import StreamlitFlowApp from "./StreamlitFlowApp";

createRoot(document.getElementById("root")).render(
	<React.StrictMode>
		<StreamlitFlowApp />
	</React.StrictMode>
);
