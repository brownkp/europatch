import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';

const KnobContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: ${props => props.size || '60px'};
  margin: ${props => props.margin || '8px'};
`;

const KnobOuter = styled.div`
  position: relative;
  width: ${props => props.size || '60px'};
  height: ${props => props.size || '60px'};
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #444, #222);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  
  &:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 100%);
    pointer-events: none;
  }
`;

const KnobInner = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  width: 4px;
  height: 40%;
  background-color: ${props => props.theme.colors.secondaryAccent || '#F7B32B'};
  transform-origin: bottom center;
  transform: translate(-50%, -100%) rotate(${props => props.rotation}deg);
`;

const KnobLabel = styled.div`
  margin-top: 4px;
  font-family: ${props => props.theme.fonts.mono || "'Courier Prime', monospace"};
  font-size: 12px;
  color: ${props => props.theme.colors.textDark || '#1A1A1A'};
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const KnobValue = styled.div`
  font-family: ${props => props.theme.fonts.mono || "'Courier Prime', monospace"};
  font-size: 10px;
  color: ${props => props.theme.colors.textDark || '#1A1A1A'};
  text-align: center;
`;

/**
 * Moog-inspired knob component for Eurorack patch generator
 * 
 * @param {Object} props - Component props
 * @param {number} props.min - Minimum value (default: 0)
 * @param {number} props.max - Maximum value (default: 100)
 * @param {number} props.value - Current value
 * @param {function} props.onChange - Change handler function
 * @param {string} props.label - Knob label
 * @param {string} props.size - Knob size (e.g., '60px')
 * @param {string} props.margin - Knob margin (e.g., '8px')
 * @param {function} props.formatValue - Function to format displayed value
 * @returns {React.Component} Knob component
 */
const Knob = ({ 
  min = 0, 
  max = 100, 
  value = 50, 
  onChange, 
  label, 
  size = '60px',
  margin = '8px',
  formatValue = val => val
}) => {
  const [rotation, setRotation] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const knobRef = useRef(null);
  const startYRef = useRef(0);
  const startValueRef = useRef(value);
  
  // Convert value to rotation (0-270 degrees)
  const valueToRotation = (val) => {
    return ((val - min) / (max - min)) * 270 - 135;
  };
  
  // Convert rotation to value
  const rotationToValue = (rot) => {
    const normalizedRotation = (rot + 135) / 270;
    return min + normalizedRotation * (max - min);
  };
  
  // Update rotation when value changes
  useEffect(() => {
    setRotation(valueToRotation(value));
  }, [value, min, max]);
  
  // Handle mouse/touch events
  const handleMouseDown = (e) => {
    setIsDragging(true);
    startYRef.current = e.clientY;
    startValueRef.current = value;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    e.preventDefault();
  };
  
  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    const deltaY = startYRef.current - e.clientY;
    const deltaValue = (deltaY / 100) * (max - min);
    let newValue = Math.min(max, Math.max(min, startValueRef.current + deltaValue));
    
    if (onChange) {
      onChange(newValue);
    }
  };
  
  const handleMouseUp = () => {
    setIsDragging(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };
  
  // Handle touch events
  const handleTouchStart = (e) => {
    setIsDragging(true);
    startYRef.current = e.touches[0].clientY;
    startValueRef.current = value;
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('touchend', handleTouchEnd);
    e.preventDefault();
  };
  
  const handleTouchMove = (e) => {
    if (!isDragging) return;
    
    const deltaY = startYRef.current - e.touches[0].clientY;
    const deltaValue = (deltaY / 100) * (max - min);
    let newValue = Math.min(max, Math.max(min, startValueRef.current + deltaValue));
    
    if (onChange) {
      onChange(newValue);
    }
    
    e.preventDefault();
  };
  
  const handleTouchEnd = () => {
    setIsDragging(false);
    document.removeEventListener('touchmove', handleTouchMove);
    document.removeEventListener('touchend', handleTouchEnd);
  };
  
  return (
    <KnobContainer size={size} margin={margin}>
      <KnobOuter 
        ref={knobRef}
        size={size}
        onMouseDown={handleMouseDown}
        onTouchStart={handleTouchStart}
      >
        <KnobInner rotation={rotation} />
      </KnobOuter>
      {label && <KnobLabel>{label}</KnobLabel>}
      <KnobValue>{formatValue(value)}</KnobValue>
    </KnobContainer>
  );
};

export default Knob;
