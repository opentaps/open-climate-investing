const dbConfig = require("../config/db.config.js");

const Sequelize = require("sequelize");
const sequelize = new Sequelize(dbConfig.DB, dbConfig.USER, dbConfig.PASSWORD, {
  host: dbConfig.HOST,
  port: dbConfig.PORT,
  dialect: dbConfig.dialect,

  pool: {
    max: dbConfig.pool.max,
    min: dbConfig.pool.min,
    acquire: dbConfig.pool.acquire,
    idle: dbConfig.pool.idle,
  },
});

const db = {};

db.Sequelize = Sequelize;
db.sequelize = sequelize;

db.carbon_risk_factor = require("./carbon_risk_factor.model.js")(sequelize, Sequelize);
db.ff_factor = require("./ff_factor.model.js")(sequelize, Sequelize);
db.stock = require("./stock.model.js")(sequelize, Sequelize);
db.stock_component = require("./stock_component.model.js")(sequelize, Sequelize);
db.stock_data = require("./stock_data.model.js")(sequelize, Sequelize);
db.stock_stat = require("./stock_stat.model.js")(sequelize, Sequelize);

module.exports = db;
