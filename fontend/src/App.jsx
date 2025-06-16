import React , { useState } from "react";
import "./styles/style.css";
import AppRoutes from "./routes/index";
import 'bootstrap/dist/css/bootstrap.min.css';


function App() {
  return (
    <div className="app">
      <AppRoutes />
    </div>
  );
}

export default App;
