module.exports = (app) => {
  const stock = require("../controllers/stock.controller.js");
  var router = require("express").Router();
  router.get("/:id", stock.findComponents);
  app.use("/api/stock_components", router);
};
