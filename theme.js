const theme = {
  colors: {
    // Panel colors
    panelBackground: '#E8D0AA',  // warm beige/tan
    woodFrame: '#8B4513',        // dark wood brown
    controlSurface: '#1A1A1A',   // near-black
    
    // Accent colors
    primaryAccent: '#D14B28',    // vintage red-orange
    secondaryAccent: '#F7B32B',  // warm amber
    tertiaryAccent: '#2D5B6B',   // deep teal
    
    // Text colors
    textDark: '#1A1A1A',         // near-black
    textLight: '#F5F5F5',        // off-white
    
    // Functional colors
    active: '#F7B32B',           // warm amber
    inactive: '#888888',         // medium gray
    
    // Patch cable colors
    cables: {
      red: '#D14B28',
      yellow: '#F7B32B',
      blue: '#2D5B6B',
      green: '#5D8233',
      purple: '#9B59B6'
    }
  },
  
  fonts: {
    heading: "'DIN Condensed', 'Roboto Condensed', sans-serif",
    body: "'Helvetica Neue', 'Inter', sans-serif",
    mono: "'Courier Prime', 'Source Code Pro', monospace"
  },
  
  shadows: {
    small: '0 2px 4px rgba(0, 0, 0, 0.1)',
    medium: '0 4px 8px rgba(0, 0, 0, 0.15)',
    large: '0 8px 16px rgba(0, 0, 0, 0.2)'
  },
  
  borders: {
    radius: {
      small: '4px',
      medium: '8px',
      large: '12px'
    }
  },
  
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px'
  },
  
  breakpoints: {
    xs: '320px',
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px'
  }
};

export default theme;
