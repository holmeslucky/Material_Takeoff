import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './app.css'
import App from './App'
import Login from './pages/Login'
import Projects from './pages/Projects'
import CreateProject from './pages/CreateProject'
import ProjectView from './pages/ProjectView'
import MaterialDatabase from './pages/MaterialDatabase'
import Templates from './pages/Templates'
import LaborRates from './pages/LaborRates'
import Settings from './pages/Settings'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/new" element={<CreateProject />} />
          <Route path="/projects/:id" element={<ProjectView />} />
          <Route path="/materials" element={<MaterialDatabase />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/labor" element={<LaborRates />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)