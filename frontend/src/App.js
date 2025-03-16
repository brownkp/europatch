import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Header from './components/layout/Header';
import Home from './pages/Home';

const AppContainer = styled.div`
  min-height: 100vh;
  background-color: #1a1a1a;
  color: #f5f5f5;
  font-family: 'Roboto', sans-serif;
`;

const Content = styled.main`
  padding-bottom: 2rem;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Header />
        <Content>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </Content>
      </AppContainer>
    </Router>
  );
}

export default App;
