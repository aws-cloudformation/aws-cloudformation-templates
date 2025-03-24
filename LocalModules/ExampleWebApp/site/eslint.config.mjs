import globals from "globals";
import pluginJs from "@eslint/js";
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended';


export default [
    {
        languageOptions: { 
            globals: globals.browser 
        }
    },
    pluginJs.configs.recommended,
    {
        ignores: ["dist", "config-sample.js", "js/vendor"]
    },
    {
        plugins: {
            "prettier": eslintPluginPrettierRecommended 
        }
    }
];
