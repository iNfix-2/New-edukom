const fs = require('node:fs');
const path = require('node:path');
const output = path.join(__dirname, '../static/vendor');
fs.mkdirSync(output, {recursive: true});
for (const [source, name] of [
 ['bootstrap/dist/css/bootstrap.min.css', 'bootstrap.min.css'],
 ['bootstrap/dist/js/bootstrap.bundle.min.js', 'bootstrap.bundle.min.js'],
 ['bootstrap-icons/font/bootstrap-icons.min.css', 'bootstrap-icons.min.css'],
 ['aos/dist/aos.css', 'aos.css'], ['aos/dist/aos.js', 'aos.js'],
 ['bootstrap/LICENSE', 'bootstrap-LICENSE'], ['bootstrap-icons/LICENSE', 'bootstrap-icons-LICENSE'], ['aos/LICENSE', 'aos-LICENSE']
]) fs.copyFileSync(path.join(__dirname, '../node_modules', source), path.join(output, name));
fs.cpSync(path.join(__dirname, '../node_modules/bootstrap-icons/font/fonts'), path.join(output, 'fonts'), {recursive: true});

for (const name of ['bootstrap-LICENSE', 'bootstrap-icons-LICENSE', 'aos-LICENSE']) { const file = path.join(output, name); fs.writeFileSync(file, fs.readFileSync(file, 'utf8').trimEnd() + '\n'); fs.chmodSync(file, 0o644); }
