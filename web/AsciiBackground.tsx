/**
 * ASCII Animation Background Component
 *
 * Usage:
 *   import { AsciiBackground } from './AsciiBackground';
 *   import { FRAMES as FRAMES_SMALL } from './frames/w20_frames';
 *   import { FRAMES as FRAMES_MED } from './frames/w58_frames';
 *
 *   <AsciiBackground
 *     frameSets={[FRAMES_SMALL, FRAMES_MED, FRAMES_SMALL, FRAMES_MED]}
 *     frameRate={200}
 *     color="#3a3a3a"
 *   />
 */

import React, { useState, useEffect, CSSProperties } from 'react';

interface AsciiBackgroundProps {
  /** Array of frame sets to cycle through (for zoom effect) */
  frameSets: string[][];
  /** Milliseconds per frame (default: 200) */
  frameRate?: number;
  /** Text color (default: #3a3a3a) */
  color?: string;
  /** Font size in pixels (default: 12) */
  fontSize?: number;
  /** Additional CSS class */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

export const AsciiBackground: React.FC<AsciiBackgroundProps> = ({
  frameSets,
  frameRate = 200,
  color = '#3a3a3a',
  fontSize = 12,
  className = '',
  style = {},
}) => {
  const [frameIndex, setFrameIndex] = useState(0);
  const [setIndex, setSetIndex] = useState(0);

  const currentFrameSet = frameSets[setIndex];
  const currentFrame = currentFrameSet[frameIndex];

  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prevFrame) => {
        const nextFrame = prevFrame + 1;

        // If we've gone through all frames, switch to next set
        if (nextFrame >= currentFrameSet.length) {
          setSetIndex((prevSet) => (prevSet + 1) % frameSets.length);
          return 0;
        }

        return nextFrame;
      });
    }, frameRate);

    return () => clearInterval(interval);
  }, [frameRate, frameSets.length, currentFrameSet.length]);

  const containerStyle: CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: -1,
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'center',
    pointerEvents: 'none',
    overflow: 'hidden',
    ...style,
  };

  const preStyle: CSSProperties = {
    fontFamily: "'Courier New', Courier, monospace",
    fontSize: `${fontSize}px`,
    lineHeight: 1.1,
    color,
    whiteSpace: 'pre',
    userSelect: 'none',
    margin: 0,
    padding: 0,
  };

  return (
    <div className={className} style={containerStyle}>
      <pre style={preStyle}>{currentFrame}</pre>
    </div>
  );
};

// ============================================================================
// Scrolling variant - tree moves across screen
// ============================================================================

interface ScrollingAsciiProps {
  /** Frames to animate */
  frames: string[];
  /** Milliseconds per frame (default: 150) */
  frameRate?: number;
  /** Scroll duration in seconds (default: 20) */
  scrollDuration?: number;
  /** Text color */
  color?: string;
  /** Font size */
  fontSize?: number;
  /** Direction: 'left' or 'right' */
  direction?: 'left' | 'right';
}

export const ScrollingAscii: React.FC<ScrollingAsciiProps> = ({
  frames,
  frameRate = 150,
  scrollDuration = 20,
  color = '#3a3a3a',
  fontSize = 12,
  direction = 'right',
}) => {
  const [frameIndex, setFrameIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setFrameIndex((prev) => (prev + 1) % frames.length);
    }, frameRate);
    return () => clearInterval(interval);
  }, [frameRate, frames.length]);

  const containerStyle: CSSProperties = {
    position: 'fixed',
    bottom: 0,
    left: 0,
    width: '100%',
    height: 'auto',
    zIndex: -1,
    pointerEvents: 'none',
    overflow: 'hidden',
  };

  const scrollStyle: CSSProperties = {
    display: 'inline-block',
    animation: `scroll-${direction} ${scrollDuration}s linear infinite`,
  };

  const preStyle: CSSProperties = {
    fontFamily: "'Courier New', Courier, monospace",
    fontSize: `${fontSize}px`,
    lineHeight: 1.1,
    color,
    whiteSpace: 'pre',
    userSelect: 'none',
    margin: 0,
  };

  // Inject keyframes if not already present
  useEffect(() => {
    const styleId = 'ascii-scroll-keyframes';
    if (!document.getElementById(styleId)) {
      const styleSheet = document.createElement('style');
      styleSheet.id = styleId;
      styleSheet.textContent = `
        @keyframes scroll-right {
          from { transform: translateX(-100%); }
          to { transform: translateX(100vw); }
        }
        @keyframes scroll-left {
          from { transform: translateX(100vw); }
          to { transform: translateX(-100%); }
        }
      `;
      document.head.appendChild(styleSheet);
    }
  }, []);

  return (
    <div style={containerStyle}>
      <div style={scrollStyle}>
        <pre style={preStyle}>{frames[frameIndex]}</pre>
      </div>
    </div>
  );
};

export default AsciiBackground;
