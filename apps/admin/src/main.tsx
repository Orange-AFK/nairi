import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App, type AdminApiClient } from "./App";

const apiClient: AdminApiClient = {
  async listPosts() {
    return [];
  }
};

const root = document.getElementById("root");

if (root) {
  createRoot(root).render(
    <StrictMode>
      <App apiClient={apiClient} />
    </StrictMode>
  );
}
