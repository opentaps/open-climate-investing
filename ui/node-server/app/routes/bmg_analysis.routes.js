
module.exports = (app) => {
  const c = require("../controllers/bmg_analysis.controller.js");
  var router = require("express").Router();
  router.get("/stocks", c.stocksWithSignificantRegressions );
  router.get("/sectors", c.sectorsWithSignificantRegressions );
  router.get("/count", c.countStocksPerSector );
  app.use("/api/bmg_analysis", router);
};
