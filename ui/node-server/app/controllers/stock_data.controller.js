const db = require("../models");
const common = require("./common.js");
const StockData = db.stock_data;
const Sequelize = db.Sequelize;
const Op = db.Sequelize.Op;

exports.findAll = (req, res) => {
  const { page, size } = req.query;

  let conditions = [];
  if (req.query["ticker"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("ticker"), {
        [Op.eq]: `${req.query["ticker"]}`,
      })
    );
  } else {
    return res.status(400).send({
      message: "No ticker parameter given.",
    });
  }
  if (req.query["from"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("date"), {
        [Op.gte]: `${req.query["from"]}`,
      })
    );
  }
  if (req.query["to"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("date"), {
        [Op.lte]: `${req.query["to"]}`,
      })
    );
  }

  const { limit, offset } = common.getPagination(page, size);

  StockData.findAndCountAll({
    where: conditions ? conditions : null,
    limit,
    offset,
  })
    .then((data) => {
      console.log(`findAll -> findAndCountAll = ${data}`);
      const response = common.getPagingData(data, page, limit);
      res.send(response);
    })
    .catch((err) => {
      res.status(500).send({
        message:
          err.message || "Some error occurred while retrieving stock data.",
      });
    });
};
