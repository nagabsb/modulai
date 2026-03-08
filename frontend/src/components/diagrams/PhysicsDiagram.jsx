import React from 'react';

/**
 * PhysicsDiagram - SVG component for various physics diagrams
 * @param {Object} props
 * @param {string} props.scene - 'inclined-plane' | 'projectile' | 'pulley' | 'buoyancy'
 * @param {number} props.angle - Angle for inclined plane or projectile (degrees)
 * @param {number} props.mass - Mass value (kg)
 * @param {number} props.m1 - Mass 1 for pulley
 * @param {number} props.m2 - Mass 2 for pulley
 * @param {number} props.v0 - Initial velocity for projectile
 */
const PhysicsDiagram = ({ 
  scene = 'inclined-plane', 
  angle = 30, 
  mass = 5,
  m1 = 5,
  m2 = 3,
  v0 = 20
}) => {
  const width = 400;
  const height = 250;

  // Arrow component for forces
  const Arrow = ({ x1, y1, x2, y2, color = 'red', label = '', labelPos = 'end' }) => {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const len = Math.sqrt(dx * dx + dy * dy);
    const ux = dx / len;
    const uy = dy / len;
    
    // Arrow head
    const headLen = 10;
    const headAngle = Math.PI / 6;
    const ax1 = x2 - headLen * (ux * Math.cos(headAngle) - uy * Math.sin(headAngle));
    const ay1 = y2 - headLen * (uy * Math.cos(headAngle) + ux * Math.sin(headAngle));
    const ax2 = x2 - headLen * (ux * Math.cos(headAngle) + uy * Math.sin(headAngle));
    const ay2 = y2 - headLen * (uy * Math.cos(headAngle) - ux * Math.sin(headAngle));
    
    const labelX = labelPos === 'end' ? x2 + ux * 15 : (x1 + x2) / 2;
    const labelY = labelPos === 'end' ? y2 + uy * 15 : (y1 + y2) / 2 - 10;
    
    return (
      <g>
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth="2" />
        <polygon points={`${x2},${y2} ${ax1},${ay1} ${ax2},${ay2}`} fill={color} />
        {label && (
          <text x={labelX} y={labelY} fontSize="12" fill={color} fontWeight="bold" textAnchor="middle">
            {label}
          </text>
        )}
      </g>
    );
  };

  // Inclined Plane Scene
  if (scene === 'inclined-plane') {
    const baseLen = 300;
    const angleRad = (angle * Math.PI) / 180;
    const planeHeight = baseLen * Math.tan(angleRad);
    const startX = 50;
    const startY = height - 30;
    
    const blockSize = 40;
    const blockX = startX + baseLen * 0.4;
    const blockY = startY - baseLen * 0.4 * Math.tan(angleRad) - blockSize;
    
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto">
        {/* Ground */}
        <line x1={20} y1={startY} x2={width - 20} y2={startY} stroke="black" strokeWidth="2" />
        
        {/* Inclined plane */}
        <line 
          x1={startX} y1={startY} 
          x2={startX + baseLen} y2={startY - planeHeight} 
          stroke="black" strokeWidth="3" 
        />
        
        {/* Angle arc */}
        <path 
          d={`M ${startX + 40} ${startY} A 40 40 0 0 0 ${startX + 40 * Math.cos(angleRad)} ${startY - 40 * Math.sin(angleRad)}`}
          fill="none" stroke="#666" strokeWidth="1"
        />
        <text x={startX + 55} y={startY - 10} fontSize="12">{angle}°</text>
        
        {/* Block */}
        <rect 
          x={blockX} y={blockY} 
          width={blockSize} height={blockSize} 
          fill="#E2E8F0" stroke="black" strokeWidth="2"
          transform={`rotate(${-angle}, ${blockX + blockSize/2}, ${blockY + blockSize/2})`}
        />
        <text 
          x={blockX + blockSize/2} y={blockY + blockSize/2 + 5} 
          fontSize="11" textAnchor="middle" fontWeight="bold"
          transform={`rotate(${-angle}, ${blockX + blockSize/2}, ${blockY + blockSize/2})`}
        >
          {mass} kg
        </text>
        
        {/* Force vectors */}
        <Arrow 
          x1={blockX + blockSize/2} y1={blockY + blockSize}
          x2={blockX + blockSize/2} y2={blockY + blockSize + 50}
          color="blue" label="W"
        />
        <Arrow 
          x1={blockX + blockSize/2} y1={blockY + blockSize/2}
          x2={blockX + blockSize/2 - 40 * Math.sin(angleRad)} y2={blockY + blockSize/2 - 40 * Math.cos(angleRad)}
          color="green" label="N"
        />
        
        {/* Title */}
        <text x={width / 2} y={20} fontSize="14" textAnchor="middle" fontWeight="bold" fill="#1E3A5F">
          Bidang Miring - Sudut {angle}°, Massa {mass} kg
        </text>
      </svg>
    );
  }

  // Projectile Motion Scene
  if (scene === 'projectile') {
    const angleRad = (angle * Math.PI) / 180;
    const g = 10;
    const maxHeight = (v0 * v0 * Math.sin(angleRad) * Math.sin(angleRad)) / (2 * g);
    const range = (v0 * v0 * Math.sin(2 * angleRad)) / g;
    
    // Scale for display
    const scale = 2;
    const startX = 50;
    const groundY = height - 40;
    
    // Generate trajectory points
    const points = [];
    const steps = 50;
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * (2 * v0 * Math.sin(angleRad) / g);
      const x = v0 * Math.cos(angleRad) * t;
      const y = v0 * Math.sin(angleRad) * t - 0.5 * g * t * t;
      points.push(`${startX + x * scale},${groundY - y * scale}`);
    }
    
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto">
        {/* Ground */}
        <line x1={20} y1={groundY} x2={width - 20} y2={groundY} stroke="black" strokeWidth="2" />
        
        {/* Trajectory path */}
        <polyline 
          points={points.join(' ')} 
          fill="none" stroke="#F4820A" strokeWidth="2" strokeDasharray="5,3"
        />
        
        {/* Initial velocity arrow */}
        <Arrow 
          x1={startX} y1={groundY}
          x2={startX + 50 * Math.cos(angleRad)} y2={groundY - 50 * Math.sin(angleRad)}
          color="red" label={`v₀=${v0} m/s`}
        />
        
        {/* Angle arc */}
        <path 
          d={`M ${startX + 30} ${groundY} A 30 30 0 0 0 ${startX + 30 * Math.cos(angleRad)} ${groundY - 30 * Math.sin(angleRad)}`}
          fill="none" stroke="#666" strokeWidth="1"
        />
        <text x={startX + 45} y={groundY - 15} fontSize="11">{angle}°</text>
        
        {/* Max height indicator */}
        <line 
          x1={startX + range * scale / 2} y1={groundY}
          x2={startX + range * scale / 2} y2={groundY - maxHeight * scale}
          stroke="#10B981" strokeWidth="1" strokeDasharray="3,3"
        />
        <text 
          x={startX + range * scale / 2 + 5} y={groundY - maxHeight * scale / 2}
          fontSize="10" fill="#10B981"
        >
          h = {maxHeight.toFixed(1)} m
        </text>
        
        {/* Range indicator */}
        <line 
          x1={startX} y1={groundY + 15}
          x2={startX + range * scale} y2={groundY + 15}
          stroke="#1E3A5F" strokeWidth="1"
        />
        <text 
          x={startX + range * scale / 2} y={groundY + 30}
          fontSize="10" fill="#1E3A5F" textAnchor="middle"
        >
          R = {range.toFixed(1)} m
        </text>
        
        {/* Title */}
        <text x={width / 2} y={20} fontSize="14" textAnchor="middle" fontWeight="bold" fill="#1E3A5F">
          Gerak Parabola - v₀={v0} m/s, θ={angle}°
        </text>
      </svg>
    );
  }

  // Pulley Scene
  if (scene === 'pulley') {
    const pulleyX = width / 2;
    const pulleyY = 60;
    const pulleyRadius = 25;
    
    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto">
        {/* Support structure */}
        <line x1={pulleyX - 60} y1={20} x2={pulleyX + 60} y2={20} stroke="black" strokeWidth="4" />
        <line x1={pulleyX} y1={20} x2={pulleyX} y2={pulleyY - pulleyRadius} stroke="black" strokeWidth="3" />
        
        {/* Pulley wheel */}
        <circle cx={pulleyX} cy={pulleyY} r={pulleyRadius} fill="#E2E8F0" stroke="black" strokeWidth="2" />
        <circle cx={pulleyX} cy={pulleyY} r="5" fill="black" />
        
        {/* Left rope and mass */}
        <line 
          x1={pulleyX - pulleyRadius} y1={pulleyY}
          x2={pulleyX - pulleyRadius} y2={height - 60}
          stroke="black" strokeWidth="2"
        />
        <rect 
          x={pulleyX - pulleyRadius - 25} y={height - 60}
          width="50" height="40"
          fill="#1E3A5F" stroke="black" strokeWidth="2"
        />
        <text 
          x={pulleyX - pulleyRadius} y={height - 35}
          fontSize="14" fill="white" textAnchor="middle" fontWeight="bold"
        >
          {m1} kg
        </text>
        
        {/* Right rope and mass */}
        <line 
          x1={pulleyX + pulleyRadius} y1={pulleyY}
          x2={pulleyX + pulleyRadius} y2={height - 80}
          stroke="black" strokeWidth="2"
        />
        <rect 
          x={pulleyX + pulleyRadius - 25} y={height - 80}
          width="50" height="40"
          fill="#F4820A" stroke="black" strokeWidth="2"
        />
        <text 
          x={pulleyX + pulleyRadius} y={height - 55}
          fontSize="14" fill="white" textAnchor="middle" fontWeight="bold"
        >
          {m2} kg
        </text>
        
        {/* Acceleration arrows */}
        {m1 > m2 ? (
          <>
            <Arrow x1={pulleyX - pulleyRadius - 40} y1={height - 40} x2={pulleyX - pulleyRadius - 40} y2={height - 10} color="red" label="a" />
            <Arrow x1={pulleyX + pulleyRadius + 40} y1={height - 60} x2={pulleyX + pulleyRadius + 40} y2={height - 90} color="red" label="a" />
          </>
        ) : (
          <>
            <Arrow x1={pulleyX - pulleyRadius - 40} y1={height - 10} x2={pulleyX - pulleyRadius - 40} y2={height - 40} color="red" label="a" />
            <Arrow x1={pulleyX + pulleyRadius + 40} y1={height - 90} x2={pulleyX + pulleyRadius + 40} y2={height - 60} color="red" label="a" />
          </>
        )}
        
        {/* Title */}
        <text x={width / 2} y={height - 5} fontSize="12" textAnchor="middle" fill="#666">
          Sistem Katrol - m₁={m1} kg, m₂={m2} kg
        </text>
      </svg>
    );
  }

  // Default/Unknown scene
  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="auto">
      <text x={width/2} y={height/2} textAnchor="middle" fill="#666">
        Diagram tidak tersedia
      </text>
    </svg>
  );
};

export default PhysicsDiagram;
