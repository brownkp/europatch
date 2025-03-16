import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';

const PatchIdeasContainer = styled.div`
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

const ButtonGroup = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const PatchIdeaCard = styled.div`
  background-color: ${props => props.theme.colors.panelBackground};
  border: 4px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.medium};
  overflow: hidden;
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.medium};
`;

const PatchIdeaHeader = styled.div`
  background-color: ${props => props.theme.colors.woodFrame};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-bottom: 2px solid ${props => props.theme.colors.controlSurface};
`;

const PatchIdeaTitle = styled.h2`
  color: ${props => props.theme.colors.textLight};
  margin: 0;
`;

const PatchIdeaContent = styled.div`
  padding: ${props => props.theme.spacing.lg};
`;

const PatchDescription = styled.p`
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

const ConnectionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const Connection = styled.div`
  background-color: ${props => props.theme.colors.textLight};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.small};
`;

const ConnectionPath = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.sm};
  font-family: ${props => props.theme.fonts.mono};
  font-weight: bold;
`;

const ConnectionModule = styled.span`
  color: ${props => props.theme.colors.textDark};
`;

const ConnectionPoint = styled.span`
  color: ${props => props.theme.colors.tertiaryAccent};
`;

const ConnectionArrow = styled.span`
  margin: 0 ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.primaryAccent};
`;

const CableColor = styled.span`
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: ${props => props.color || props.theme.colors.primaryAccent};
  margin-right: ${props => props.theme.spacing.sm};
`;

const ConnectionDescription = styled.p`
  margin: 0;
  font-style: italic;
`;

const ControlSettingsList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const ControlSetting = styled.div`
  background-color: ${props => props.theme.colors.textLight};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.small};
`;

const ControlSettingHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ControlName = styled.span`
  font-family: ${props => props.theme.fonts.mono};
  font-weight: bold;
  color: ${props => props.theme.colors.textDark};
`;

const ControlValue = styled.span`
  margin-left: auto;
  font-family: ${props => props.theme.fonts.mono};
  color: ${props => props.theme.colors.primaryAccent};
`;

const SourcesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const Source = styled.div`
  background-color: ${props => props.theme.colors.textLight};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.small};
`;

const SourceType = styled.span`
  display: inline-block;
  background-color: ${props => {
    switch (props.type) {
      case 'reddit':
        return '#FF4500';
      case 'modwiggler':
        return '#4B6EAF';
      default:
        return props.theme.colors.tertiaryAccent;
    }
  }};
  color: ${props => props.theme.colors.textLight};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borders.radius.small};
  font-size: 0.8rem;
  font-weight: bold;
  margin-right: ${props => props.theme.spacing.sm};
`;

const SourceTitle = styled.span`
  font-weight: bold;
`;

const SourceLink = styled.a`
  display: block;
  margin-top: ${props => props.theme.spacing.xs};
  font-family: ${props => props.theme.fonts.mono};
  font-size: 0.9rem;
  color: ${props => props.theme.colors.tertiaryAccent};
  
  &:hover {
    color: ${props => props.theme.colors.primaryAccent};
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

const PatchDiagram = styled.div`
  background-color: ${props => props.theme.colors.controlSurface};
  border-radius: ${props => props.theme.borders.radius.small};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.lg};
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.textLight};
  font-style: italic;
`;

const PatchIdeasPage = () => {
  const { rackId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [patchIdeas, setPatchIdeas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    // If patch ideas were passed via location state, use them
    if (location.state && location.state.patchIdeas) {
      setPatchIdeas(location.state.patchIdeas);
      setLoading(false);
      return;
    }
    
    // Otherwise, fetch them from the API
    const fetchPatchIdeas = async () => {
      try {
        // In a real implementation, we would fetch patch ideas from the API
        // For now, we'll just redirect to the rack analysis page
        navigate(`/rack/${rackId}`);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    fetchPatchIdeas();
  }, [rackId, location.state, navigate]);
  
  if (loading) {
    return (
      <LoadingContainer>
        <div style={{ width: '50px', height: '50px', border: '5px solid #E8D0AA', borderTopColor: '#D14B28', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <LoadingText>Loading patch ideas...</LoadingText>
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
        <Button onClick={() => navigate(`/rack/${rackId}`)}>Back to Rack</Button>
      </div>
    );
  }
  
  return (
    <PatchIdeasContainer>
      <PageHeader>
        <h1>Patch Ideas</h1>
        <ButtonGroup>
          <Button secondary onClick={() => navigate(`/rack/${rackId}`)}>Back to Rack</Button>
          <Button onClick={() => navigate('/')}>New Rack</Button>
        </ButtonGroup>
      </PageHeader>
      
      {patchIdeas.length === 0 ? (
        <p>No patch ideas found. Try generating some from the rack analysis page.</p>
      ) : (
        patchIdeas.map((idea, index) => (
          <PatchIdeaCard key={index}>
            <PatchIdeaHeader>
              <PatchIdeaTitle>{idea.title}</PatchIdeaTitle>
            </PatchIdeaHeader>
            <PatchIdeaContent>
              <PatchDescription>{idea.description}</PatchDescription>
              
              <PatchDiagram>
                [Visual patch diagram would be rendered here]
              </PatchDiagram>
              
              <SectionTitle>Connections</SectionTitle>
              <ConnectionsList>
                {idea.connections.map((connection, connIndex) => (
                  <Connection key={connIndex}>
                    <ConnectionPath>
                      <CableColor color={connection.cable_color} />
                      <ConnectionModule>{connection.source_module.name}</ConnectionModule>
                      <ConnectionPoint> ({connection.source_connection.name})</ConnectionPoint>
                      <ConnectionArrow>→</ConnectionArrow>
                      <ConnectionModule>{connection.target_module.name}</ConnectionModule>
                      <ConnectionPoint> ({connection.target_connection.name})</ConnectionPoint>
                    </ConnectionPath>
                    <ConnectionDescription>{connection.description}</ConnectionDescription>
                  </Connection>
                ))}
              </ConnectionsList>
              
              <SectionTitle>Knob Settings</SectionTitle>
              <ControlSettingsList>
                {idea.control_settings.map((setting, settingIndex) => (
                  <ControlSetting key={settingIndex}>
                    <ControlSettingHeader>
                      <ControlName>{setting.module.name} {setting.control.name}</ControlName>
                      <ControlValue>{setting.value_text}</ControlValue>
                    </ControlSettingHeader>
                    <p>{setting.description}</p>
                  </ControlSetting>
                ))}
              </ControlSettingsList>
              
              {idea.sources && idea.sources.length > 0 && (
                <>
                  <SectionTitle>Sources</SectionTitle>
                  <SourcesList>
                    {idea.sources.map((source, sourceIndex) => (
                      <Source key={sourceIndex}>
                        <div>
                          <SourceType type={source.type}>{source.type}</SourceType>
                          <SourceTitle>{source.title || 'Source'}</SourceTitle>
                        </div>
                        {source.url && (
                          <SourceLink href={source.url} target="_blank" rel="noopener noreferrer">
                            {source.url}
                          </SourceLink>
                        )}
                      </Source>
                    ))}
                  </SourcesList>
                </>
              )}
            </PatchIdeaContent>
          </PatchIdeaCard>
        ))
      )}
      
      <Button fullWidth onClick={() => navigate(`/rack/${rackId}`)}>
        Generate More Patch Ideas
      </Button>
    </PatchIdeasContainer>
  );
};

export default PatchIdeasPage;
