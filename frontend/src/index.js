import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { GoogleOAuthProvider } from "@react-oauth/google";

const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID || "";

// Log unhandled promise rejections (e.g. API errors) for debugging; skip 401 from /auth/me
window.addEventListener("unhandledrejection", (event) => {
  const status = event.reason?.response?.status;
  if (status === 401 && event.reason?.config?.url?.includes?.("/auth/me")) return;
  if (event.reason?.response) return; // Let axios interceptor / UI handle it
  console.error("Unhandled rejection:", event.reason);
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>,
);
