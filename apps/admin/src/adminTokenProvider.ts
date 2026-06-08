export type AdminTokenProvider = {
  getAuthToken: () => string;
};

export function createAdminTokenProvider(): AdminTokenProvider {
  return {
    getAuthToken() {
      return "";
    }
  };
}
