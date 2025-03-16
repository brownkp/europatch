import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';

const KnobContainer = styled.div`
  position: relative;
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  user-select: none;
`;

const KnobOuter = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: ${props => props.backgroundColor || '#333'};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
`;

const KnobInner = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  width: ${props => props.size * (1 - props.thickness * 2)}px;
  height: ${props => props.size * (1 - props.thickness * 2)}px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(circle at 40% 40%, #444, #222);
  box-shadow: inset 0 2px 3px rgba(0, 0, 0, 0.4);
`;

const KnobIndicator = styled.div`
  position: absolute;
  top: ${props => props.size / 2 - props.size * 0.05}px;
  left: 50%;
  width: 2px;
  height: ${props => props.size * 0.3}px;
  background-color: ${props => props.color || '#f5f5f5'};
  transform-origin: bottom center;
  transform: translateX(-50%) rotate(${props => props.rotation}deg);
`;

const KnobTicks = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
`;

const KnobTick = styled.div`
  position: absolute;
  top: ${props => props.size * 0.05}px;
  left: 50%;
  width: 1px;
  height: ${props => props.size * 0.1}px;
  background-color: ${props => props.isMajor ? '#f5f5f5' : 'rgba(255, 255, 255, 0.3)'};
  transform-origin: bottom center;
  transform: translateX(-50%) rotate(${props => props.rotation}deg);
`;

const KnobName = styled.div`
  position: absolute;
  bottom: -20px;
  left: 0;
  width: 100%;
  text-align: center;
  font-size: 12px;
  color: #f5f5f5;
`;

export const Knob = ({
  value = 0,
  min = 0,
  max = 100,
  size = 60,
  thickness = 0.2,
  color = '#f5f5f5',
  backgroundColor = '#333',
  onChange,
  name
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [startValue, setStartValue] = useState(value);

  // Calculate rotation based on value
  const minAngle = -150;
  const maxAngle = 150;
  const angleRange = maxAngle - minAngle;
  const valueRange = max - min;
  const rotation = minAngle + (value - min) / valueRange * angleRange;

  // Use useCallback to memoize the event handlers
  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;

    const deltaY = startY - e.clientY;
    const deltaValue = (deltaY / 100) * valueRange;
    let newValue = startValue + deltaValue;

    // Clamp value to min/max
    newValue = Math.max(min, Math.min(max, newValue));

    if (onChange) {
      onChange(newValue);
    }
  }, [isDragging, startY, startValue, valueRange, min, max, onChange]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  }, [handleMouseMove]);

  // Handle mouse/touch events
  const handleMouseDown = (e) => {
    if (!onChange) return;

    setIsDragging(true);
    setStartY(e.clientY);
    setStartValue(value);

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Clean up event listeners
  useEffect(() => {
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);
  
  // Generate tick marks
  const ticks = [];
  const tickCount = 11; // Number of ticks
  
  for (let i = 0; i < tickCount; i++) {
    const tickRotation = minAngle + (i / (tickCount - 1)) * angleRange;
    const isMajor = i === 0 || i === Math.floor(tickCount / 2) || i === tickCount - 1;
    
    ticks.push(
      <KnobTick 
        key={i} 
        rotation={tickRotation} 
        isMajor={isMajor} 
        size={size} 
      />
    );
  }
  
  return (
    <KnobContainer 
      size={size} 
      onMouseDown={handleMouseDown}
    >
      <KnobOuter backgroundColor={backgroundColor}>
        <KnobTicks>
          {ticks}
        </KnobTicks>
      </KnobOuter>
      <KnobInner size={size} thickness={thickness} />
      <KnobIndicator 
        rotation={rotation} 
        color={color} 
        size={size} 
      />
      {name && <KnobName>{name}</KnobName>}
    </KnobContainer>
  );
};
