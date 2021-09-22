module.exports = (app) => {
  const stock = require("../controllers/stock.controller.js");
  var router = require("express").Router();
  router.get("/", stock.findAll);
  router.get("/:id", stock.findOne);
  app.use("/api/stocks", router);
};
