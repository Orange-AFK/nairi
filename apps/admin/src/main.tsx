import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { createAdminApiClient } from "./adminApiClient";

const apiClient = createAdminApiClient({
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? ""
});

const root = document.getElementById("root");

if (root) {
  createRoot(root).render(
    <StrictMode>
      <App apiClient={apiClient} />
    </StrictMode>
  );
}
