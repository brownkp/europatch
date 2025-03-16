import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled, { ThemeProvider } from 'styled-components';
import GlobalStyle from './styles/globalStyles';
import theme from './styles/theme';

// Pages
import HomePage from './pages/HomePage';
import RackAnalysisPage from './pages/RackAnalysisPage';
import PatchIdeasPage from './pages/PatchIdeasPage';
import ModuleDetailPage from './pages/ModuleDetailPage';

// Components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: ${props => props.theme.colors.panelBackground};
`;

const ContentContainer = styled.main`
  flex: 1;
  padding: ${props => props.theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Header />
          <ContentContainer>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/rack/:rackId" element={<RackAnalysisPage />} />
              <Route path="/patches/:rackId" element={<PatchIdeasPage />} />
              <Route path="/module/:moduleId" element={<ModuleDetailPage />} />
            </Routes>
          </ContentContainer>
          <Footer />
        </AppContainer>
      </Router>
    </ThemeProvider>
  );
}

export default App;
