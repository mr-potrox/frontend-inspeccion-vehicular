// eslint.config.js
import js from "@eslint/js";
import globals from "globals";
import react from "eslint-plugin-react";
import tseslint from "typescript-eslint";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: "./tsconfig.json",
      },
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    plugins: {
      react,
    },
    rules: {
      "react/react-in-jsx-scope": "off", // No hace falta en React 17+
      "react/prop-types": "off",        // Usamos TS en vez de PropTypes
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },
];
