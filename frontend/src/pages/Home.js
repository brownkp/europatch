import React, { useState } from 'react';
import styled from 'styled-components';
import { Knob } from '../components/Knob';

const HomeContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  color: #e87500;
  margin-bottom: 2rem;
  font-family: 'Helvetica Neue', sans-serif;
`;

const ModularGridForm = styled.form`
  background-color: #2c2c2c;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border: 1px solid #444;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border-radius: 4px;
  background-color: #1a1a1a;
  border: 1px solid #444;
  color: #f5f5f5;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #e87500;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 0.75rem;
  border-radius: 4px;
  background-color: #1a1a1a;
  border: 1px solid #444;
  color: #f5f5f5;
  font-size: 1rem;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: #e87500;
  }
`;

const Button = styled.button`
  background-color: #e87500;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #d56c00;
  }
  
  &:disabled {
    background-color: #666;
    cursor: not-allowed;
  }
`;

const ResultsContainer = styled.div`
  background-color: #2c2c2c;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #444;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
`;

const ModuleList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const Module = styled.div`
  background-color: #1a1a1a;
  border-radius: 6px;
  padding: 1rem;
  border: 1px solid #444;
`;

const ModuleName = styled.h3`
  margin-top: 0;
  color: #e87500;
`;

const PatchIdea = styled.div`
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #444;
`;

const PatchTitle = styled.h2`
  color: #e87500;
  margin-bottom: 1rem;
`;

const PatchDescription = styled.p`
  margin-bottom: 1.5rem;
  line-height: 1.6;
`;

const ConnectionList = styled.div`
  margin-bottom: 2rem;
`;

const Connection = styled.div`
  background-color: #1a1a1a;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border: 1px solid #444;
`;

const KnobSettings = styled.div`
  margin-top: 2rem;
`;

const KnobContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-top: 1rem;
`;

const KnobWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
`;

const KnobLabel = styled.div`
  margin-top: 0.5rem;
  text-align: center;
  font-size: 0.9rem;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  
  &:after {
    content: " ";
    display: block;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 6px solid #e87500;
    border-color: #e87500 transparent #e87500 transparent;
    animation: spinner 1.2s linear infinite;
  }
  
  @keyframes spinner {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const SourcesList = styled.div`
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #444;
  font-size: 0.9rem;
`;

const Home = () => {
  const [modulargridUrl, setModulargridUrl] = useState('');
  const [patchPrompt, setPatchPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [patchResult, setPatchResult] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!modulargridUrl) return;
    
    setLoading(true);
    setPatchResult(null);
    
    try {
      // Call the backend API to parse the ModularGrid rack
      const response = await fetch('/api/parse-rack', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modulargrid_url: modulargridUrl }),
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      
      const rackData = await response.json();
      
      // If we have a prompt, generate a patch idea
      let patchData = null;
      if (patchPrompt && rackData.modules && rackData.modules.length > 0) {
        const patchResponse = await fetch('/api/generate-patch', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            modules: rackData.modules.map(module => module.id),
            prompt: patchPrompt,
          }),
        });
        
        if (patchResponse.ok) {
          patchData = await patchResponse.json();
        }
      }
      
      // Format the result to match the expected structure
      const result = {
        modules: rackData.modules || [],
        patch: patchData || {
          title: "Your Rack",
          description: "Your ModularGrid rack has been loaded. Add a patch prompt to generate patch ideas.",
          connections: [],
          knobSettings: [],
          sources: []
        }
      };
      
      setPatchResult(result);
      setLoading(false);
      
    } catch (error) {
      console.error("Error generating patch:", error);
      setLoading(false);
      alert(`Failed to fetch rack data: ${error.message}`);
    }
  };
  
  return (
    <HomeContainer>
      <Title>Generate Eurorack Patch Ideas</Title>
      
      <ModularGridForm onSubmit={handleSubmit}>
        <FormGroup>
          <Label htmlFor="modulargrid-url">ModularGrid Rack URL</Label>
          <Input
            id="modulargrid-url"
            type="text"
            value={modulargridUrl}
            onChange={(e) => setModulargridUrl(e.target.value)}
            placeholder="https://www.modulargrid.net/e/racks/view/123456"
            required
          />
        </FormGroup>
        
        <FormGroup>
          <Label htmlFor="patch-prompt">Patch Idea Prompt</Label>
          <TextArea
            id="patch-prompt"
            value={patchPrompt}
            onChange={(e) => setPatchPrompt(e.target.value)}
            placeholder="Describe the type of patch you want to create (e.g., 'ambient drone with slowly evolving textures')"
          />
        </FormGroup>
        
        <Button type="submit" disabled={loading || !modulargridUrl}>
          {loading ? 'Generating...' : 'Generate Patch Ideas'}
        </Button>
      </ModularGridForm>
      
      {loading && <LoadingSpinner />}
      
      {patchResult && (
        <ResultsContainer>
          <Title>Your Rack</Title>
          
          <ModuleList>
            {patchResult.modules.map((module) => (
              <Module key={module.id}>
                <ModuleName>{module.name}</ModuleName>
                <p><strong>Manufacturer:</strong> {module.manufacturer}</p>
                <p><strong>Type:</strong> {module.type}</p>
                <p>{module.description}</p>
              </Module>
            ))}
          </ModuleList>
          
          <PatchIdea>
            <PatchTitle>{patchResult.patch.title}</PatchTitle>
            <PatchDescription>{patchResult.patch.description}</PatchDescription>
            
            <h3>Patch Connections</h3>
            <ConnectionList>
              {patchResult.patch.connections.map((connection, index) => (
                <Connection key={index}>
                  <p><strong>{connection.source} → {connection.target}</strong></p>
                  <p>{connection.description}</p>
                </Connection>
              ))}
            </ConnectionList>
            
            <KnobSettings>
              <h3>Suggested Knob Settings</h3>
              <KnobContainer>
                {patchResult.patch.knobSettings.map((knob, index) => (
                  <KnobWrapper key={index}>
                    <Knob 
                      value={50} 
                      min={0}
                      max={100}
                      size={80}
                      thickness={0.2}
                      color="#e87500"
                      backgroundColor="#1a1a1a"
                      name={knob.knob}
                    />
                    <KnobLabel>
                      <strong>{knob.module} - {knob.knob}</strong>
                      <div>{knob.value}</div>
                    </KnobLabel>
                  </KnobWrapper>
                ))}
              </KnobContainer>
            </KnobSettings>
            
            <SourcesList>
              <h3>Sources</h3>
              <ul>
                {patchResult.patch.sources.map((source, index) => (
                  <li key={index}>
                    <a href={source} target="_blank" rel="noopener noreferrer">
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </SourcesList>
          </PatchIdea>
        </ResultsContainer>
      )}
    </HomeContainer>
  );
};

export default Home;
