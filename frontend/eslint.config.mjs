import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";
import pluginJs from "@eslint/js";
import unusedImports from "eslint-plugin-unused-imports";
import prettier from "eslint-plugin-prettier";
import prettierConfig from "eslint-config-prettier";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: pluginJs.configs.recommended,
});

export default [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  prettierConfig,
  {
    plugins: {
      "unused-imports": unusedImports,
      prettier: prettier,
    },
    rules: {
      "prettier/prettier": "error",
      "complexity": ["error", { "max": 10 }],
      "max-depth": ["error", 4],
      "max-params": ["error", 5],
      "unused-imports/no-unused-imports": "error",
      "unused-imports/no-unused-vars": [
        "warn",
        {
          vars: "all",
          varsIgnorePattern: "^_",
          args: "after-used",
          argsIgnorePattern: "^_",
        },
      ],
    },
  },
  {
    ignores: [
      "node_modules/",
      ".next/",
      "out/",
      "dist/",
      "build/",
      "public/",
      "coverage/",
      "*.config.js",
      "*.config.mjs",
    ],
  },
];
