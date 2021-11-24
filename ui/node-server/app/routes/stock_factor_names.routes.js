module.exports = (app) => {
  const stockStats = require("../controllers/stock_stats.controller.js");
  var router = require("express").Router();
  router.get("/", stockStats.findFactorNames);
  app.use("/api/factor_names", router);
};
