# Running tests

## Start storybook
```
npm run storybook
```

## Run tests
Note: individual tests may also be run directly in the storybook UI
```
npm run test-storybook
```

## View HTML coverage report
### Generate report
```
npx nyc report --reporter=lcov -t coverage/storybook --report-dir coverage/storybook
```
### View in browser
```
open coverage/storybook/lcov-report/index.html
```

## Accessibility tests
To change which accessibility violations trigger test failures, update the `includedImpacts` setting in `.storybook/test-runner.js`
Possible values: "minor", "moderate", "serious", or "critical"
