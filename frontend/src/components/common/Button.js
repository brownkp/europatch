import React from 'react';
import styled from 'styled-components';

const ButtonContainer = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background-color: ${props => props.secondary ? props.theme.colors.tertiaryAccent : props.theme.colors.primaryAccent};
  color: ${props => props.theme.colors.textLight};
  border: none;
  border-radius: ${props => props.theme.borders.radius.small};
  font-family: ${props => props.theme.fonts.heading};
  font-size: 1rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
  width: ${props => props.fullWidth ? '100%' : 'auto'};
  position: relative;
  
  &:hover {
    background-color: ${props => props.secondary ? props.theme.colors.secondaryAccent : props.theme.colors.secondaryAccent};
    box-shadow: ${props => props.theme.shadows.medium};
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
    box-shadow: ${props => props.theme.shadows.small};
  }
  
  &:disabled {
    background-color: ${props => props.theme.colors.inactive};
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: ${props => props.theme.borders.radius.small};
    background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 50%, rgba(0,0,0,0.1) 100%);
    pointer-events: none;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  margin-right: ${props => props.theme.spacing.sm};
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: ${props => props.theme.colors.textLight};
  animation: spin 1s ease-in-out infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const Button = ({ 
  children, 
  onClick, 
  type = 'button', 
  secondary = false, 
  fullWidth = false, 
  disabled = false,
  loading = false,
  ...props 
}) => {
  return (
    <ButtonContainer 
      type={type} 
      onClick={onClick} 
      secondary={secondary} 
      fullWidth={fullWidth} 
      disabled={disabled || loading}
      {...props}
    >
      {loading && <LoadingSpinner />}
      {children}
    </ButtonContainer>
  );
};

export default Button;
