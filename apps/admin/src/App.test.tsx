import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { App, type AdminApiClient } from "./App";

function adminApiClient(): AdminApiClient {
  return {
    async listPosts() {
      return [
        {
          id: "post-1",
          title: "First draft",
          status: "draft",
          updatedAt: "2026-06-08T00:00:00Z"
        }
      ];
    }
  };
}

describe("Nairi admin console shell", () => {
  it("switches between reserved admin modules without leaving the injected API boundary", async () => {
    const user = userEvent.setup();
    render(<App apiClient={adminApiClient()} />);

    const navigation = screen.getByRole("navigation", { name: "Admin modules" });
    const contentModule = screen.getByRole("link", { name: "Content" });

    expect(navigation).toBeInTheDocument();
    expect(contentModule).toHaveAttribute("aria-current", "page");
    expect(await screen.findByRole("heading", { name: "Content workspace" })).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "Media" }));
    expect(screen.getByRole("link", { name: "Media" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("heading", { name: "Media library" })).toBeInTheDocument();
    expect(screen.getByText("Media workflows remain reserved for a later boundary.")).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "Settings" }));
    expect(screen.getByRole("link", { name: "Settings" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("heading", { name: "System settings" })).toBeInTheDocument();
    expect(screen.getByText("Settings workflows remain reserved for a later boundary.")).toBeInTheDocument();
  });

  it("loads draft content through an injected API client", async () => {
    render(<App apiClient={adminApiClient()} />);

    expect(screen.getByRole("heading", { name: "Nairi Admin" })).toBeInTheDocument();
    expect(screen.getByText("Loading admin content…")).toBeInTheDocument();

    expect(await screen.findByRole("button", { name: /First draft/ })).toBeInTheDocument();
    expect(screen.getAllByText("draft").length).toBeGreaterThan(0);
  });

  it("selects a post without bypassing the injected API boundary", async () => {
    const user = userEvent.setup();
    render(<App apiClient={adminApiClient()} />);

    await user.click(await screen.findByRole("button", { name: /First draft/ }));

    expect(screen.getByRole("heading", { name: "First draft" })).toBeInTheDocument();
    expect(screen.getByText("API-backed draft preview"));
  });

  it("renders a safe error state when injected post loading fails", async () => {
    render(
      <App
        apiClient={{
          async listPosts() {
            throw new Error("network unavailable");
          }
        }}
      />
    );

    expect(await screen.findByText("Admin content could not be loaded."));
    expect(screen.queryByText("Loading admin content…")).not.toBeInTheDocument();
  });
});
