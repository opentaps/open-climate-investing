module.exports = (app) => {
  const stockStats = require("../controllers/stock_stats.controller.js");
  var router = require("express").Router();
  router.get("/", stockStats.findAll);
  app.use("/api/stats", router);
};
