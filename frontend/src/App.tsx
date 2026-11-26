import { Route, Routes, useLocation } from "react-router";
import { RequireAuth } from "./auth/AuthProvider";
import { AppLayout } from "./components/AppLayout";
import { rememberInitialLocation } from "./components/navigation";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export function App() {
  rememberInitialLocation(useLocation().key);

  return (
    <Routes>
      <Route path="/logg-inn" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route
            path="forslag"
            element={
              <PlaceholderPage title="Bestillingsforslag og meldinger" />
            }
          />
          <Route path="mrp" element={<PlaceholderPage title="MRP-tabell" />} />
          <Route
            path="mrp/:vare"
            element={<PlaceholderPage title="MRP-tabell" />}
          />
          <Route path="bom" element={<PlaceholderPage title="BOM-tre" />} />
          <Route
            path="plan"
            element={<PlaceholderPage title="MPS og lager" />}
          />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
