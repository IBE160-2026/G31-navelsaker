import { Route, Routes } from "react-router";
import { RequireAuth } from "./auth/AuthProvider";
import { LoginPage } from "./pages/LoginPage";
import { SignedInPage } from "./pages/SignedInPage";

export function App() {
  return (
    <Routes>
      <Route path="/logg-inn" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route path="*" element={<SignedInPage />} />
      </Route>
    </Routes>
  );
}
