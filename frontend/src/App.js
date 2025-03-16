import React, { useState } from 'react';
import styled from 'styled-components';
import Header from './components/layout/Header';
import Home from './pages/Home';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
`;

const ContentContainer = styled.main`
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

function App() {
  return (
    <AppContainer>
      <Header />
      <ContentContainer>
        <Home />
      </ContentContainer>
    </AppContainer>
  );
}

export default App;
