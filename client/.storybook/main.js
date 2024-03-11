/** @type { import('@storybook/react-webpack5').StorybookConfig } */
const config = {
    stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
    
    addons: [
      "@storybook/addon-links",
      "@storybook/addon-essentials",
      "@storybook/preset-create-react-app",
      "@storybook/addon-onboarding",
      "@storybook/addon-interactions",
      '@storybook/addon-styling',
      'storybook-addon-react-router-v6',
      '@storybook/addon-a11y',
      '@storybook/addon-coverage'
    ],
    
    framework: {
      name: "@storybook/react-webpack5",
      options: {},
    },
    
    docs: {
      autodocs: "tag",
    },
    
    staticDirs: ["../public"],
  
    // Extend Webpack configuration to work better with TypeScript
    webpackFinal: async (config) => {
      // Modify or add a rule for TypeScript files
      config.module.rules.push({
        test: /\.(ts|tsx)$/,
        loader: require.resolve('babel-loader'),
        options: {
          presets: [['react-app', { flow: false, typescript: true }]],
        },
      });
  
      config.resolve.extensions.push('.ts', '.tsx');
      
      return config;
    },
  };
  
  export default config;
