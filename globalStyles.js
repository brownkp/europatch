import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: ${props => props.theme.fonts.body};
    color: ${props => props.theme.colors.textDark};
    background-color: ${props => props.theme.colors.panelBackground};
    line-height: 1.6;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: ${props => props.theme.fonts.heading};
    margin-bottom: ${props => props.theme.spacing.md};
    color: ${props => props.theme.colors.textDark};
  }

  h1 {
    font-size: 2.5rem;
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  h2 {
    font-size: 2rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }

  h3 {
    font-size: 1.5rem;
    letter-spacing: 1px;
  }

  p {
    margin-bottom: ${props => props.theme.spacing.md};
  }

  a {
    color: ${props => props.theme.colors.primaryAccent};
    text-decoration: none;
    transition: color 0.2s ease;

    &:hover {
      color: ${props => props.theme.colors.secondaryAccent};
    }
  }

  button {
    font-family: ${props => props.theme.fonts.heading};
    cursor: pointer;
  }

  input, textarea {
    font-family: ${props => props.theme.fonts.body};
  }

  code, pre {
    font-family: ${props => props.theme.fonts.mono};
  }
`;

export default GlobalStyle;
