module.exports = (app) => {
  const stock = require("../controllers/stock.controller.js");
  var router = require("express").Router();
  router.get("/:id", stock.findParents);
  app.use("/api/stock_parents", router);
};
