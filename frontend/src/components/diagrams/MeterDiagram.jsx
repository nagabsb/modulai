import React from 'react';

/**
 * MeterDiagram - SVG component for ammeter/voltmeter displays
 * @param {Object} props
 * @param {string} props.type - 'ammeter' or 'voltmeter'
 * @param {number} props.needlePosition - Position of needle (0-100)
 * @param {string} props.range - Range text like "0.5 A" or "10 V"
 */
const MeterDiagram = ({ type = 'ammeter', needlePosition = 50, range = '1 A' }) => {
  // Ensure range is always a string
  const rangeStr = String(range);
  const width = 200;
  const height = 150;
  const centerX = width / 2;
  const centerY = height - 30;
  const radius = 70;
  
  // Calculate needle angle (-120 to 120 degrees, mapped from 0-100)
  const startAngle = -120;
  const endAngle = 120;
  const angleRange = endAngle - startAngle;
  const needleAngle = startAngle + (needlePosition / 100) * angleRange;
  const needleRad = (needleAngle * Math.PI) / 180;
  
  // Needle endpoint
  const needleLength = radius - 10;
  const needleEndX = centerX + needleLength * Math.sin(needleRad);
  const needleEndY = centerY - needleLength * Math.cos(needleRad);
  
  // Generate scale ticks
  const ticks = [];
  const labels = [];
  const numTicks = 11; // 0, 10, 20, ... 100
  
  for (let i = 0; i < numTicks; i++) {
    const tickValue = (i / (numTicks - 1)) * 100;
    const tickAngle = startAngle + (tickValue / 100) * angleRange;
    const tickRad = (tickAngle * Math.PI) / 180;
    
    const innerRadius = radius - 8;
    const outerRadius = i % 2 === 0 ? radius : radius - 4;
    
    const x1 = centerX + innerRadius * Math.sin(tickRad);
    const y1 = centerY - innerRadius * Math.cos(tickRad);
    const x2 = centerX + outerRadius * Math.sin(tickRad);
    const y2 = centerY - outerRadius * Math.cos(tickRad);
    
    ticks.push(
      <line 
        key={`tick-${i}`}
        x1={x1} y1={y1} x2={x2} y2={y2}
        stroke="black" 
        strokeWidth={i % 2 === 0 ? 2 : 1}
      />
    );
    
    // Add labels for major ticks
    if (i % 2 === 0) {
      const labelRadius = radius + 12;
      const labelX = centerX + labelRadius * Math.sin(tickRad);
      const labelY = centerY - labelRadius * Math.cos(tickRad);
      
      labels.push(
        <text
          key={`label-${i}`}
          x={labelX}
          y={labelY}
          fontSize="10"
          textAnchor="middle"
          dominantBaseline="middle"
        >
          {Math.round(tickValue)}
        </text>
      );
    }
  }
  
  // Arc path for meter face
  const arcStartRad = (startAngle * Math.PI) / 180;
  const arcEndRad = (endAngle * Math.PI) / 180;
  const arcStartX = centerX + radius * Math.sin(arcStartRad);
  const arcStartY = centerY - radius * Math.cos(arcStartRad);
  const arcEndX = centerX + radius * Math.sin(arcEndRad);
  const arcEndY = centerY - radius * Math.cos(arcEndRad);
  
  const meterSymbol = type === 'ammeter' ? 'A' : 'V';
  const meterColor = type === 'ammeter' ? '#1E3A5F' : '#10B981';
  
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto" className="meter-diagram">
      {/* Background circle/arc */}
      <path
        d={`M ${arcStartX} ${arcStartY} A ${radius} ${radius} 0 1 1 ${arcEndX} ${arcEndY}`}
        fill="none"
        stroke="#E2E8F0"
        strokeWidth="20"
      />
      
      {/* Meter arc outline */}
      <path
        d={`M ${arcStartX} ${arcStartY} A ${radius} ${radius} 0 1 1 ${arcEndX} ${arcEndY}`}
        fill="none"
        stroke={meterColor}
        strokeWidth="2"
      />
      
      {/* Scale ticks */}
      {ticks}
      
      {/* Scale labels */}
      {labels}
      
      {/* Needle */}
      <line
        x1={centerX}
        y1={centerY}
        x2={needleEndX}
        y2={needleEndY}
        stroke="red"
        strokeWidth="2"
        strokeLinecap="round"
      />
      
      {/* Needle center dot */}
      <circle cx={centerX} cy={centerY} r="6" fill={meterColor} />
      <circle cx={centerX} cy={centerY} r="3" fill="white" />
      
      {/* Meter type symbol */}
      <circle cx={centerX} cy={centerY - 30} r="12" fill="none" stroke={meterColor} strokeWidth="2" />
      <text
        x={centerX}
        y={centerY - 26}
        fontSize="14"
        fontWeight="bold"
        textAnchor="middle"
        fill={meterColor}
      >
        {meterSymbol}
      </text>
      
      {/* Range label */}
      <text
        x={centerX}
        y={height - 5}
        fontSize="11"
        textAnchor="middle"
        fill="#666"
      >
        Skala: 0 - {rangeStr}
      </text>
      
      {/* Current reading indicator */}
      <text
        x={centerX}
        y={centerY + 20}
        fontSize="10"
        textAnchor="middle"
        fill="#666"
      >
        Pembacaan: {((needlePosition / 100) * parseFloat(rangeStr)).toFixed(2)} {rangeStr.split(' ')[1] || ''}
      </text>
    </svg>
  );
};

export default MeterDiagram;
