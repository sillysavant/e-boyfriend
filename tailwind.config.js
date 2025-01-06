module.exports = {
  // ... other config
  theme: {
    extend: {
      keyframes: {
        "float-up": {
          "0%": { transform: "translateY(20px)", opacity: 0 },
          "100%": { transform: "translateY(0)", opacity: 1 },
        },
      },
      animation: {
        "float-up": "float-up 0.3s ease-out forwards",
      },
    },
  },
};
