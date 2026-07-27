const fs = require('fs');
const path = require('path');

/**
 * This script updates README.md by replacing the content between
 * <!--START_SECTION:activity--> and <!--END_SECTION:activity-->
 * with a small generated block that changes every run.
 *
 * If the markers don't exist, it appends the block to the end.
 */

function generateActivityMarkdown() {
  const now = new Date().toISOString();
  const random = Math.floor(Math.random() * 1000000);

  return `<!--START_SECTION:activity-->

## Automated activity

- Last updated: ${now}
- Activity token: **${random}**

<!--END_SECTION:activity-->`;
}

function main() {
  const readmePath = path.join(process.cwd(), 'README.md');
  let readme = '';
  try {
    readme = fs.readFileSync(readmePath, 'utf8');
  } catch (err) {
    console.log('README.md not found, creating a new one.');
    readme = '# Amirullah\n\n';
  }

  const startMarker = '<!--START_SECTION:activity-->';
  const endMarker = '<!--END_SECTION:activity-->';

  const generated = generateActivityMarkdown();

  if (readme.includes(startMarker) && readme.includes(endMarker)) {
    // replace existing section
    const before = readme.split(startMarker)[0];
    const after = readme.split(endMarker)[1];
    const newReadme = before + generated + after;
    fs.writeFileSync(readmePath, newReadme, 'utf8');
    console.log('Replaced existing activity section in README.md');
  } else {
    // append the section at the end
    const newReadme = readme.trimEnd() + '\n\n' + generated + '\n';
    fs.writeFileSync(readmePath, newReadme, 'utf8');
    console.log('Appended activity section to README.md');
  }
}

main();
