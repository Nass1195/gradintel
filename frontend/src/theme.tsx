import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
    },
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
    },
    "ul": {
      listStyleType: "disc",
      paddingInlineStart: "1.5rem",
    },
    "ol": {
      listStyleType: "decimal",
      paddingInlineStart: "1.5rem",
    },
    ".typing-indicator": {
      display: "inline-flex",
      alignItems: "center",
      gap: "0.25rem",
    },
    ".typing-indicator-dot": {
      width: "6px",
      height: "6px",
      borderRadius: "9999px",
      backgroundColor: "#A0AEC0",
      animation: "typingBounce 1.2s infinite ease-in-out",
    },
    ".typing-indicator-dot:nth-of-type(2)": {
      animationDelay: "0.2s",
    },
    ".typing-indicator-dot:nth-of-type(3)": {
      animationDelay: "0.4s",
    },
    "@keyframes typingBounce": {
      "0%, 80%, 100%": {
        transform: "scale(0.6)",
        opacity: 0.4,
      },
      "40%": {
        transform: "scale(1)",
        opacity: 1,
      },
    },
  },
  theme: {
    tokens: {
      colors: {
        ui: {
          main: { value: "#009688" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})
