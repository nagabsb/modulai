import React from 'react';

/**
 * CircuitDiagram - SVG component for electrical circuit diagrams
 * @param {Object} props
 * @param {number[]} props.resistors - Array of resistor values in Ohms
 * @param {number} props.voltage - Voltage value in Volts
 * @param {string} props.type - 'series' or 'parallel'
 */
const CircuitDiagram = ({ resistors = [2, 3], voltage = 12, type = 'series' }) => {
  const width = 400;
  const height = type === 'parallel' ? 250 : 200;

  // Battery component
  const Battery = ({ x, y, v }) => (
    <g transform={`translate(${x}, ${y})`}>
      {/* Long line (positive) */}
      <line x1="0" y1="-15" x2="0" y2="15" stroke="black" strokeWidth="3" />
      {/* Short line (negative) */}
      <line x1="10" y1="-8" x2="10" y2="8" stroke="black" strokeWidth="2" />
      {/* Plus sign */}
      <text x="-10" y="-10" fontSize="12" fontWeight="bold">+</text>
      {/* Minus sign */}
      <text x="15" y="5" fontSize="12" fontWeight="bold">-</text>
      {/* Voltage label */}
      <text x="-5" y="35" fontSize="11" textAnchor="middle">{v}V</text>
    </g>
  );

  // Resistor (zigzag) component
  const Resistor = ({ x, y, value, horizontal = true }) => {
    const zigzag = horizontal 
      ? "M0,0 L5,-8 L15,8 L25,-8 L35,8 L45,-8 L55,8 L60,0"
      : "M0,0 L-8,5 L8,15 L-8,25 L8,35 L-8,45 L8,55 L0,60";
    
    return (
      <g transform={`translate(${x}, ${y})`}>
        <path d={zigzag} fill="none" stroke="black" strokeWidth="2" />
        <text 
          x={horizontal ? 30 : 20} 
          y={horizontal ? -15 : 30} 
          fontSize="11" 
          textAnchor="middle"
        >
          {value}Ω
        </text>
      </g>
    );
  };

  // Wire (line) component
  const Wire = ({ x1, y1, x2, y2 }) => (
    <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="black" strokeWidth="2" />
  );

  // Dot (connection point)
  const Dot = ({ x, y }) => (
    <circle cx={x} cy={y} r="4" fill="black" />
  );

  if (type === 'series') {
    // Series circuit layout
    const startX = 50;
    const startY = 100;
    const resistorWidth = 60;
    const spacing = 30;
    
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto" className="circuit-diagram">
        {/* Top wire */}
        <Wire x1={startX} y1={startY - 50} x2={width - startX} y2={startY - 50} />
        
        {/* Battery on left side */}
        <Wire x1={startX} y1={startY - 50} x2={startX} y2={startY - 20} />
        <Battery x={startX - 5} y={startY} v={voltage} />
        <Wire x1={startX} y1={startY + 20} x2={startX} y2={startY + 50} />
        
        {/* Bottom wire with resistors */}
        <Wire x1={startX} y1={startY + 50} x2={startX + spacing} y2={startY + 50} />
        
        {resistors.map((r, i) => {
          const rx = startX + spacing + i * (resistorWidth + spacing);
          return (
            <React.Fragment key={i}>
              <Resistor x={rx} y={startY + 50} value={r} horizontal={true} />
              {i < resistors.length - 1 && (
                <Wire 
                  x1={rx + resistorWidth} 
                  y1={startY + 50} 
                  x2={rx + resistorWidth + spacing} 
                  y2={startY + 50} 
                />
              )}
            </React.Fragment>
          );
        })}
        
        {/* Right side connection */}
        <Wire 
          x1={startX + spacing + resistors.length * resistorWidth + (resistors.length - 1) * spacing} 
          y1={startY + 50} 
          x2={width - startX} 
          y2={startY + 50} 
        />
        <Wire x1={width - startX} y1={startY + 50} x2={width - startX} y2={startY - 50} />
        
        {/* Current direction arrow */}
        <path 
          d="M200,35 L210,40 L200,45" 
          fill="none" 
          stroke="red" 
          strokeWidth="2" 
        />
        <text x="215" y="43" fontSize="10" fill="red">I</text>
        
        {/* Title */}
        <text x={width / 2} y={height - 10} fontSize="12" textAnchor="middle" fill="#666">
          Rangkaian Seri - R total = {resistors.reduce((a, b) => a + b, 0)}Ω
        </text>
      </svg>
    );
  } else {
    // Parallel circuit layout
    const startX = 50;
    const centerY = height / 2;
    const branchSpacing = 60;
    
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto" className="circuit-diagram">
        {/* Battery on left */}
        <Wire x1={startX} y1={40} x2={startX} y2={centerY - 20} />
        <Battery x={startX - 5} y={centerY} v={voltage} />
        <Wire x1={startX} y1={centerY + 20} x2={startX} y2={height - 40} />
        
        {/* Top horizontal wire */}
        <Wire x1={startX} y1={40} x2={width - startX} y2={40} />
        
        {/* Bottom horizontal wire */}
        <Wire x1={startX} y1={height - 40} x2={width - startX} y2={height - 40} />
        
        {/* Right vertical wire */}
        <Wire x1={width - startX} y1={40} x2={width - startX} y2={height - 40} />
        
        {/* Parallel branches */}
        {resistors.map((r, i) => {
          const branchX = 120 + i * 100;
          const topY = 40;
          const bottomY = height - 40;
          const resistorY = (topY + bottomY) / 2 - 30;
          
          return (
            <g key={i}>
              <Dot x={branchX} y={topY} />
              <Wire x1={branchX} y1={topY} x2={branchX} y2={resistorY} />
              <Resistor x={branchX} y={resistorY} value={r} horizontal={false} />
              <Wire x1={branchX} y1={resistorY + 60} x2={branchX} y2={bottomY} />
              <Dot x={branchX} y={bottomY} />
            </g>
          );
        })}
        
        {/* Current arrows */}
        <path d="M70,60 L80,65 L70,70" fill="none" stroke="red" strokeWidth="2" />
        <text x="85" y="68" fontSize="10" fill="red">I</text>
        
        {/* Title */}
        <text x={width / 2} y={height - 10} fontSize="12" textAnchor="middle" fill="#666">
          Rangkaian Paralel - 1/R total = {resistors.map(r => `1/${r}`).join(' + ')}
        </text>
      </svg>
    );
  }
};

export default CircuitDiagram;
