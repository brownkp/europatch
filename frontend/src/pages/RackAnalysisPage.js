import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';
import Knob from '../components/common/Knob';

const RackAnalysisContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xl};
`;

const RackHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  @media (max-width: ${props => props.theme.breakpoints.md}) {
    flex-direction: column;
    align-items: flex-start;
    gap: ${props => props.theme.spacing.md};
  }
`;

const RackInfo = styled.div``;

const RackTitle = styled.h1`
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const RackUrl = styled.a`
  color: ${props => props.theme.colors.tertiaryAccent};
  font-family: ${props => props.theme.fonts.mono};
  font-size: 0.9rem;
  
  &:hover {
    color: ${props => props.theme.colors.primaryAccent};
  }
`;

const ModulesContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const ModuleCard = styled.div`
  background-color: ${props => props.theme.colors.controlSurface};
  border: 4px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.medium};
  overflow: hidden;
  box-shadow: ${props => props.theme.shadows.medium};
`;

const ModuleImage = styled.img`
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-bottom: 2px solid ${props => props.theme.colors.woodFrame};
`;

const ModuleInfo = styled.div`
  padding: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.textLight};
`;

const ModuleName = styled.h3`
  margin-bottom: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.textLight};
`;

const ModuleManufacturer = styled.p`
  font-size: 0.9rem;
  margin-bottom: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.secondaryAccent};
`;

const ModuleType = styled.span`
  display: inline-block;
  background-color: ${props => props.theme.colors.tertiaryAccent};
  color: ${props => props.theme.colors.textLight};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borders.radius.small};
  font-size: 0.8rem;
  font-weight: bold;
`;

const PatchForm = styled.div`
  background-color: ${props => props.theme.colors.panelBackground};
  border: 4px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.medium};
  padding: ${props => props.theme.spacing.lg};
  margin-top: ${props => props.theme.spacing.xl};
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

const Textarea = styled.textarea`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.woodFrame};
  border-radius: ${props => props.theme.borders.radius.small};
  font-family: ${props => props.theme.fonts.body};
  font-size: 1rem;
  background-color: ${props => props.theme.colors.textLight};
  min-height: 100px;
  resize: vertical;
  
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

const ComplexityContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ComplexityLabel = styled.p`
  font-family: ${props => props.theme.fonts.heading};
  font-weight: bold;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const ComplexityValue = styled.p`
  font-family: ${props => props.theme.fonts.mono};
  font-size: 0.9rem;
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

const RackAnalysisPage = () => {
  const { rackId } = useParams();
  const navigate = useNavigate();
  const [rackData, setRackData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [prompt, setPrompt] = useState('');
  const [complexity, setComplexity] = useState(3);
  const [generating, setGenerating] = useState(false);
  
  useEffect(() => {
    const fetchRackData = async () => {
      try {
        const response = await fetch(`/api/rack/${rackId}`);
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch rack data');
        }
        
        setRackData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRackData();
  }, [rackId]);
  
  const handleGeneratePatch = async (e) => {
    e.preventDefault();
    
    if (!prompt) {
      setError('Please enter a patch description');
      return;
    }
    
    setGenerating(true);
    setError('');
    
    try {
      const response = await fetch('/api/patch/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rack_id: rackId,
          prompt,
          complexity,
          max_results: 3
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate patch ideas');
      }
      
      // Navigate to patch ideas page
      navigate(`/patches/${rackId}`, { state: { patchIdeas: data.patch_ideas } });
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };
  
  if (loading) {
    return (
      <LoadingContainer>
        <div style={{ width: '50px', height: '50px', border: '5px solid #E8D0AA', borderTopColor: '#D14B28', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <LoadingText>Loading rack data...</LoadingText>
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
    <RackAnalysisContainer>
      <RackHeader>
        <RackInfo>
          <RackTitle>{rackData.rack_name}</RackTitle>
          <RackUrl href={rackData.modulargrid_url} target="_blank" rel="noopener noreferrer">
            {rackData.modulargrid_url}
          </RackUrl>
        </RackInfo>
        <Button onClick={() => navigate('/')}>Back to Home</Button>
      </RackHeader>
      
      <div>
        <h2>Detected Modules</h2>
        <ModulesContainer>
          {rackData.modules.map(module => (
            <ModuleCard key={module.id}>
              {module.image_url && (
                <ModuleImage src={module.image_url} alt={`${module.manufacturer} ${module.name}`} />
              )}
              <ModuleInfo>
                <ModuleName>{module.name}</ModuleName>
                <ModuleManufacturer>{module.manufacturer}</ModuleManufacturer>
                <ModuleType>{module.module_type}</ModuleType>
              </ModuleInfo>
            </ModuleCard>
          ))}
        </ModulesContainer>
      </div>
      
      <PatchForm>
        <h2>Generate Patch Ideas</h2>
        <form onSubmit={handleGeneratePatch}>
          <FormGroup>
            <Label htmlFor="prompt">What kind of patch would you like to create?</Label>
            <Textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the type of patch you want to create..."
              disabled={generating}
            />
            <ExampleText>
              Examples: "Generative ambient with random melodies", "Techno beat with acid bassline", 
              "Drone with evolving textures"
            </ExampleText>
          </FormGroup>
          
          <ComplexityContainer>
            <ComplexityLabel>Patch Complexity</ComplexityLabel>
            <Knob
              min={1}
              max={5}
              value={complexity}
              onChange={setComplexity}
              formatValue={val => `${Math.round(val)}`}
            />
            <ComplexityValue>Level {Math.round(complexity)}</ComplexityValue>
          </ComplexityContainer>
          
          {error && <ErrorMessage>{error}</ErrorMessage>}
          
          <Button type="submit" fullWidth loading={generating}>
            {generating ? 'Generating Patch Ideas...' : 'Generate Patch Ideas'}
          </Button>
        </form>
      </PatchForm>
    </RackAnalysisContainer>
  );
};

export default RackAnalysisPage;
