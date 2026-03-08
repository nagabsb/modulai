import React from 'react';
import { CircuitDiagram, MeterDiagram, PhysicsDiagram } from '../components/diagrams';

/**
 * Parse diagram tags from AI-generated content and replace with React components
 * Tag format: [DIAGRAM:type,param1=value1,param2=value2,...]
 * 
 * Examples:
 * [DIAGRAM:circuit,type=series,R1=2,R2=3,V=12]
 * [DIAGRAM:meter,type=ammeter,needle=70,range=0.5 A]
 * [DIAGRAM:physics,scene=inclined-plane,angle=30,mass=5]
 */

/**
 * Parse a single diagram tag and extract parameters
 * @param {string} tag - The diagram tag string
 * @returns {Object|null} - Parsed parameters or null if invalid
 */
const parseDiagramTag = (tag) => {
  // Remove brackets and DIAGRAM: prefix
  const content = tag.replace(/^\[DIAGRAM:/, '').replace(/\]$/, '');
  const parts = content.split(',');
  
  if (parts.length === 0) return null;
  
  const diagramType = parts[0].trim();
  const params = {};
  
  parts.slice(1).forEach(part => {
    const [key, value] = part.split('=').map(s => s.trim());
    if (key && value !== undefined) {
      // Try to parse as number
      const numValue = parseFloat(value);
      params[key] = isNaN(numValue) ? value : numValue;
    }
  });
  
  return { type: diagramType, params };
};

/**
 * Render a diagram component based on parsed tag
 * @param {Object} diagram - Parsed diagram object with type and params
 * @param {number} key - Unique key for React
 * @returns {JSX.Element} - React component
 */
const renderDiagram = (diagram, key) => {
  if (!diagram) return null;
  
  const { type, params } = diagram;
  
  switch (type) {
    case 'circuit':
      const resistors = [];
      if (params.R1) resistors.push(params.R1);
      if (params.R2) resistors.push(params.R2);
      if (params.R3) resistors.push(params.R3);
      
      return (
        <div key={key} className="my-4 p-4 bg-white rounded-lg border border-slate-200">
          <CircuitDiagram 
            resistors={resistors.length > 0 ? resistors : [2, 3]}
            voltage={params.V || params.voltage || 12}
            type={params.type || 'series'}
          />
        </div>
      );
      
    case 'meter':
      return (
        <div key={key} className="my-4 p-4 bg-white rounded-lg border border-slate-200 max-w-xs mx-auto">
          <MeterDiagram 
            type={params.type || 'ammeter'}
            needlePosition={params.needle || params.needlePosition || 50}
            range={params.range || '1 A'}
          />
        </div>
      );
      
    case 'physics':
      return (
        <div key={key} className="my-4 p-4 bg-white rounded-lg border border-slate-200">
          <PhysicsDiagram 
            scene={params.scene || 'inclined-plane'}
            angle={params.angle || 30}
            mass={params.mass || 5}
            m1={params.m1 || 5}
            m2={params.m2 || 3}
            v0={params.v0 || 20}
          />
        </div>
      );
      
    default:
      return null;
  }
};

/**
 * Process HTML content and replace diagram tags with React components
 * @param {string} html - HTML content with diagram tags
 * @returns {JSX.Element[]} - Array of React elements
 */
export const parseDiagramsInContent = (html) => {
  if (!html) return [<span key="empty"></span>];
  
  // Regex to find diagram tags
  const diagramRegex = /\[DIAGRAM:[^\]]+\]/g;
  
  // Split content by diagram tags
  const parts = html.split(diagramRegex);
  const matches = html.match(diagramRegex) || [];
  
  const elements = [];
  
  parts.forEach((part, index) => {
    // Add text part
    if (part) {
      elements.push(
        <span key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part }} />
      );
    }
    
    // Add diagram if there's a matching tag
    if (matches[index]) {
      const diagram = parseDiagramTag(matches[index]);
      const diagramElement = renderDiagram(diagram, `diagram-${index}`);
      if (diagramElement) {
        elements.push(diagramElement);
      }
    }
  });
  
  return elements;
};

/**
 * Check if content contains any diagram tags
 * @param {string} html - HTML content
 * @returns {boolean}
 */
export const hasDiagrams = (html) => {
  if (!html) return false;
  return /\[DIAGRAM:[^\]]+\]/.test(html);
};

/**
 * Remove diagram tags from content (for export/print without diagrams)
 * @param {string} html - HTML content
 * @returns {string} - HTML without diagram tags
 */
export const removeDiagramTags = (html) => {
  if (!html) return '';
  return html.replace(/\[DIAGRAM:[^\]]+\]/g, '');
};

/**
 * Extract all diagram configurations from content
 * @param {string} html - HTML content
 * @returns {Array} - Array of diagram configurations
 */
export const extractDiagrams = (html) => {
  if (!html) return [];
  
  const matches = html.match(/\[DIAGRAM:[^\]]+\]/g) || [];
  return matches.map(parseDiagramTag).filter(Boolean);
};

export default parseDiagramsInContent;
