module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [0],  // Disable line length limit for body
    'footer-max-line-length': [0],  // Disable line length limit for footer
  },
};
