import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';

const ModuleDetailContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xl};
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${props => props.theme.spacing.md};
  }
`;

const ModuleCard = styled.div`
  display: flex;
  flex-direction: column;
  background-color: ${props => props.theme.colors.panelBackground};
  border: 4px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.medium};
  overflow: hidden;
  box-shadow: ${props => props.theme.shadows.medium};
  
  @media (min-width: ${props => props.theme.breakpoints.md}) {
    flex-direction: row;
  }
`;

const ModuleImageContainer = styled.div`
  flex: 0 0 300px;
  background-color: ${props => props.theme.colors.controlSurface};
  padding: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    flex: 0 0 200px;
  }
`;

const ModuleImage = styled.img`
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
`;

const ModuleInfo = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.lg};
`;

const ModuleManufacturer = styled.h2`
  color: ${props => props.theme.colors.primaryAccent};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ModuleName = styled.h1`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ModuleType = styled.span`
  display: inline-block;
  background-color: ${props => props.theme.colors.tertiaryAccent};
  color: ${props => props.theme.colors.textLight};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borders.radius.small};
  font-size: 0.9rem;
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ModuleDescription = styled.p`
  margin-bottom: ${props => props.theme.spacing.lg};
  font-size: 1.1rem;
`;

const SectionTitle = styled.h3`
  margin-top: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.textDark};
  border-bottom: 2px solid ${props => props.theme.colors.woodFrame};
  padding-bottom: ${props => props.theme.spacing.xs};
`;

const ConnectionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const ConnectionItem = styled.div`
  background-color: ${props => props.type === 'input' ? props.theme.colors.textLight : props.theme.colors.controlSurface};
  color: ${props => props.type === 'input' ? props.theme.colors.textDark : props.theme.colors.textLight};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.small};
`;

const ConnectionName = styled.div`
  font-family: ${props => props.theme.fonts.mono};
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ConnectionType = styled.span`
  display: inline-block;
  background-color: ${props => {
    switch (props.type) {
      case 'input':
        return props.theme.colors.tertiaryAccent;
      case 'output':
        return props.theme.colors.primaryAccent;
      default:
        return props.theme.colors.secondaryAccent;
    }
  }};
  color: ${props => props.theme.colors.textLight};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borders.radius.small};
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ControlsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const ControlItem = styled.div`
  background-color: ${props => props.theme.colors.textLight};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.small};
`;

const ControlName = styled.div`
  font-family: ${props => props.theme.fonts.mono};
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ControlType = styled.span`
  display: inline-block;
  background-color: ${props => props.theme.colors.secondaryAccent};
  color: ${props => props.theme.colors.textDark};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borders.radius.small};
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ManualLink = styled.a`
  display: inline-block;
  margin-top: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.primaryAccent};
  font-weight: bold;
  
  &:hover {
    color: ${props => props.theme.colors.secondaryAccent};
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl} 0;
`;

const LoadingText = styled.p`
  font-size: 1.2rem;
  margin-top: ${props => props.theme.spacing.lg};
`;

const ModuleDetailPage = () => {
  const { moduleId } = useParams();
  const navigate = useNavigate();
  const [moduleData, setModuleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        const response = await fetch(`/api/module/${moduleId}`);
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch module data');
        }
        
        setModuleData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchModuleData();
  }, [moduleId]);
  
  if (loading) {
    return (
      <LoadingContainer>
        <div style={{ width: '50px', height: '50px', border: '5px solid #E8D0AA', borderTopColor: '#D14B28', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <LoadingText>Loading module data...</LoadingText>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </LoadingContainer>
    );
  }
  
  if (error) {
    return (
      <div>
        <h2>Error</h2>
        <p>{error}</p>
        <Button onClick={() => navigate('/')}>Back to Home</Button>
      </div>
    );
  }
  
  return (
    <ModuleDetailContainer>
      <PageHeader>
        <h1>Module Details</h1>
        <Button onClick={() => navigate(-1)}>Back</Button>
      </PageHeader>
      
      <ModuleCard>
        <ModuleImageContainer>
          {moduleData.image_url ? (
            <ModuleImage src={moduleData.image_url} alt={`${moduleData.manufacturer} ${moduleData.name}`} />
          ) : (
            <div>No image available</div>
          )}
        </ModuleImageContainer>
        
        <ModuleInfo>
          <ModuleManufacturer>{moduleData.manufacturer}</ModuleManufacturer>
          <ModuleName>{moduleData.name}</ModuleName>
          <ModuleType>{moduleData.module_type}</ModuleType>
          
          {moduleData.description && (
            <ModuleDescription>{moduleData.description}</ModuleDescription>
          )}
          
          {moduleData.hp_width && (
            <p><strong>Width:</strong> {moduleData.hp_width} HP</p>
          )}
          
          {moduleData.manual_url && (
            <ManualLink href={moduleData.manual_url} target="_blank" rel="noopener noreferrer">
              View Manual
            </ManualLink>
          )}
        </ModuleInfo>
      </ModuleCard>
      
      {moduleData.connections && moduleData.connections.length > 0 && (
        <>
          <SectionTitle>Connections</SectionTitle>
          <ConnectionsGrid>
            {moduleData.connections.map((connection, index) => (
              <ConnectionItem key={index} type={connection.type}>
                <ConnectionName>{connection.name}</ConnectionName>
                <ConnectionType type={connection.type}>
                  {connection.type.toUpperCase()}
                </ConnectionType>
                {connection.description && <p>{connection.description}</p>}
                {connection.voltage_range && (
                  <p><strong>Voltage Range:</strong> {connection.voltage_range}</p>
                )}
              </ConnectionItem>
            ))}
          </ConnectionsGrid>
        </>
      )}
      
      {moduleData.controls && moduleData.controls.length > 0 && (
        <>
          <SectionTitle>Controls</SectionTitle>
          <ControlsGrid>
            {moduleData.controls.map((control, index) => (
              <ControlItem key={index}>
                <ControlName>{control.name}</ControlName>
                <ControlType>{control.type}</ControlType>
                {control.description && <p>{control.description}</p>}
                {(control.min_value !== undefined && control.max_value !== undefined) && (
                  <p><strong>Range:</strong> {control.min_value} to {control.max_value}</p>
                )}
                {control.default_value !== undefined && (
                  <p><strong>Default:</strong> {control.default_value}</p>
                )}
              </ControlItem>
            ))}
          </ControlsGrid>
        </>
      )}
    </ModuleDetailContainer>
  );
};

export default ModuleDetailPage;
