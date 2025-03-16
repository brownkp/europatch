import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

const HeaderContainer = styled.header`
  background-color: #2c2c2c;
  padding: 1rem 2rem;
  border-bottom: 2px solid #e87500;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  font-family: 'Helvetica Neue', sans-serif;
  font-weight: bold;
  font-size: 1.8rem;
  color: #e87500;
  display: flex;
  align-items: center;
  
  span {
    margin-left: 0.5rem;
  }
`;

const WoodPanel = styled.div`
  background: linear-gradient(to bottom, #8B4513, #A0522D);
  border-radius: 5px;
  padding: 0.5rem 1rem;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
`;

const Navigation = styled.nav`
  ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  
  li {
    margin-left: 1.5rem;
  }
  
  a {
    color: #f5f5f5;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
    
    &:hover {
      color: #e87500;
    }
  }
`;

const Header = () => {
  return (
    <HeaderContainer>
      <Logo>
        <WoodPanel>EURO</WoodPanel>
        <span>PATCH</span>
      </Logo>
      <Navigation>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/about">About</Link>
          </li>
        </ul>
      </Navigation>
    </HeaderContainer>
  );
};

export default Header;
