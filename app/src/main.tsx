import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

// Curated variable fonts — the active --font-* slots are chosen per profile by
// the theme engine (see theme/themeMap.ts).
import "@fontsource-variable/fraunces/index.css";
import "@fontsource-variable/manrope/index.css";
import "@fontsource-variable/newsreader/index.css";
import "@fontsource-variable/mulish/index.css";
import "@fontsource-variable/roboto-slab/index.css";
import "@fontsource-variable/work-sans/index.css";
import "@fontsource-variable/space-grotesk/index.css";
import "@fontsource-variable/inter/index.css";
import "@fontsource-variable/bitter/index.css";
import "@fontsource/space-mono/400.css";
import "@fontsource/space-mono/700.css";
import "./index.css";

import App from "./App.tsx";
import { ProfileProvider } from "./theme/ProfileContext.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ProfileProvider>
        <App />
      </ProfileProvider>
    </BrowserRouter>
  </StrictMode>,
);
