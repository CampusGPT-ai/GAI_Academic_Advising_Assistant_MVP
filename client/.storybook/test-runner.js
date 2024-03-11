const { getStoryContext } = require('@storybook/test-runner');
const { injectAxe, checkA11y } = require('axe-playwright');

/*
 * See https://storybook.js.org/docs/writing-tests/test-runner#test-hook-api
 * to learn more about the test-runner hooks API.
 */
module.exports = {
  async preVisit(page) {
    await injectAxe(page);
  },
  async postVisit(page, context) {
    const storyContext = await getStoryContext(page, context);

    // Do not run a11y tests on disabled stories.
    if (storyContext.parameters?.a11y?.disable) {
      return;
    }
    await checkA11y(page, '#storybook-root', {
      includedImpacts: ['critical'],
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });
  },
};
