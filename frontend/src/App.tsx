import { Route, Routes, useLocation } from "react-router";
import { RequireAuth } from "./auth/AuthProvider";
import { AppLayout } from "./components/AppLayout";
import { rememberInitialLocation } from "./components/navigation";
import { LoginPage } from "./pages/LoginPage";
import { SignedInPage } from "./pages/SignedInPage";

export function App() {
  rememberInitialLocation(useLocation().key);

  return (
    <Routes>
      <Route path="/logg-inn" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route path="*" element={<SignedInPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
