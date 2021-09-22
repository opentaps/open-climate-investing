module.exports = (app) => {
  const stockData = require("../controllers/stock_data.controller.js");
  var router = require("express").Router();
  router.get("/", stockData.findAll);
  app.use("/api/data", router);
};
