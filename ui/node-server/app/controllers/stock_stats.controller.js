const db = require("../models");
const common = require("./common.js");
const StockStat = db.stock_stat;
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
  }

  const { limit, offset } = common.getPagination(page, size);

  StockStat.findAndCountAll({
    where: conditions ? conditions : null,
    limit,
    offset,
    order: ["ticker", "from_date"],
  })
    .then((data) => {
      console.log(`findAll -> findAndCountAll = ${data}`);
      const response = common.getPagingData(data, page, limit);
      res.send(response);
    })
    .catch((err) => {
      res.status(500).send({
        message:
          err.message || "Some error occurred while retrieving stock stats.",
      });
    });
};
