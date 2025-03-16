import React from 'react';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: ${props => props.theme.colors.woodFrame};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.textLight};
  margin-top: auto;
`;

const FooterContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    flex-direction: column;
    gap: ${props => props.theme.spacing.md};
  }
`;

const Copyright = styled.div`
  font-size: 0.9rem;
`;

const FooterLinks = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const FooterLink = styled.a`
  color: ${props => props.theme.colors.textLight};
  font-size: 0.9rem;
  text-decoration: none;
  
  &:hover {
    color: ${props => props.theme.colors.secondaryAccent};
  }
`;

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <FooterContainer>
      <FooterContent>
        <Copyright>
          © {currentYear} Eurorack Patch Generator. All rights reserved.
        </Copyright>
        <FooterLinks>
          <FooterLink href="https://github.com/yourusername/eurorack-patch-generator" target="_blank" rel="noopener noreferrer">
            GitHub
          </FooterLink>
          <FooterLink href="/privacy">Privacy Policy</FooterLink>
          <FooterLink href="/terms">Terms of Service</FooterLink>
        </FooterLinks>
      </FooterContent>
    </FooterContainer>
  );
};

export default Footer;
