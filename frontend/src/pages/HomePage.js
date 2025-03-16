import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';

const HomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: ${props => props.theme.spacing.xl} 0;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.textDark};
`;

const Subtitle = styled.p`
  text-align: center;
  font-size: 1.2rem;
  max-width: 600px;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const FormContainer = styled.div`
  background-color: ${props => props.theme.colors.panelBackground};
  border: 4px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.medium};
  padding: ${props => props.theme.spacing.xl};
  width: 100%;
  max-width: 600px;
  box-shadow: ${props => props.theme.shadows.medium};
`;

const FormGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${props => props.theme.spacing.sm};
  font-family: ${props => props.theme.fonts.heading};
  font-weight: bold;
  color: ${props => props.theme.colors.textDark};
`;

const Input = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.small};
  font-family: ${props => props.theme.fonts.body};
  font-size: 1rem;
  background-color: ${props => props.theme.colors.textLight};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primaryAccent};
  }
`;

const ExampleText = styled.p`
  font-size: 0.9rem;
  color: ${props => props.theme.colors.textDark};
  margin-top: ${props => props.theme.spacing.xs};
  font-style: italic;
`;

const ErrorMessage = styled.p`
  color: ${props => props.theme.colors.primaryAccent};
  margin-top: ${props => props.theme.spacing.xs};
  font-size: 0.9rem;
`;

const HomePage = () => {
  const [rackUrl, setRackUrl] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate URL
    if (!rackUrl) {
      setError('Please enter a ModularGrid rack URL');
      return;
    }
    
    if (!rackUrl.includes('modulargrid.net/e/racks/view/')) {
      setError('Please enter a valid ModularGrid rack URL');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/rack/parse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: rackUrl }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to parse rack');
      }
      
      // Navigate to rack analysis page
      navigate(`/rack/${data.rack_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <HomeContainer>
      <Title>EURORACK PATCH GENERATOR</Title>
      <Subtitle>
        Generate creative patch ideas for your Eurorack modular synthesizer based on your ModularGrid rack.
      </Subtitle>
      
      <FormContainer>
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="rackUrl">ModularGrid Rack URL</Label>
            <Input
              id="rackUrl"
              type="text"
              value={rackUrl}
              onChange={(e) => setRackUrl(e.target.value)}
              placeholder="https://www.modulargrid.net/e/racks/view/12345"
              disabled={isLoading}
            />
            <ExampleText>Example: https://www.modulargrid.net/e/racks/view/12345</ExampleText>
            {error && <ErrorMessage>{error}</ErrorMessage>}
          </FormGroup>
          
          <Button type="submit" fullWidth loading={isLoading}>
            {isLoading ? 'Analyzing Rack...' : 'Analyze Rack'}
          </Button>
        </form>
      </FormContainer>
    </HomeContainer>
  );
};

export default HomePage;
