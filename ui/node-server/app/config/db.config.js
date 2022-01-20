const fs = require('fs');
const ini = require('ini');

let filepath = './';

// lookup the config
let depth = 1;
while (!fs.existsSync(filepath + 'db.ini')) {
  if (filepath.length == 2) filepath = '../';
  else filepath = '../' + filepath;
  depth++;
  if (depth > 10) {
    throw new Error('Cannot file the DB config file db.ini');
  }
}
let config = ini.parse(fs.readFileSync(filepath + 'db.ini', 'utf-8'));
console.log('Found DB config: ', filepath+'db.ini');


module.exports = {
  HOST: config.DEFAULT.databasehost,
  USER: config.DEFAULT.databaseuser,
  PASSWORD: config.DEFAULT.databasepassword,
  PORT: config.DEFAULT.databaseport || 5432,
  DB: config.DEFAULT.databasename,
  dialect: "postgres",
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000,
  },
};
