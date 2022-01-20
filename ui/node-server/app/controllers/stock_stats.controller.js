const db = require("../models");
const common = require("./common.js");
const StockStat = db.stock_stat;
const Sequelize = db.Sequelize;
const Op = db.Sequelize.Op;

exports.findFrequencies = (req, res) => {
  let conditions = [];
  if (req.query["ticker"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("ticker"), {
        [Op.eq]: `${req.query["ticker"]}`,
      })
    );
  }
  StockStat.findAll({
    where: conditions ? conditions : null,
    attributes: [
      // specify an array where the first element is the SQL function and the second is the alias
      [
        Sequelize.fn("DISTINCT", Sequelize.col("frequency")),
        "frequency",
      ],
    ],
  })
    .then((data) => {
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message:
          err.message ||
          "Some error occurred while retrieving stock stats frequencies.",
      });
    });
};

exports.findFactorNames = (req, res) => {
  let conditions = [];
  if (req.query["ticker"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("ticker"), {
        [Op.eq]: `${req.query["ticker"]}`,
      })
    );
  }
  StockStat.findAll({
    where: conditions ? conditions : null,
    attributes: [
      // specify an array where the first element is the SQL function and the second is the alias
      [
        Sequelize.fn("DISTINCT", Sequelize.col("bmg_factor_name")),
        "factor_name",
      ],
    ],
  })
    .then((data) => {
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message:
          err.message ||
          "Some error occurred while retrieving stock stats factor names.",
      });
    });
};

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
  let factor_name = req.query["factorName"] || req.query["factor_name"] || req.query["bmg_factor_name"] || "DEFAULT";
  let frequency = req.query["frequency"] || 'MONTHLY';
  console.log(`stock_stats.controller::findAll -> factor_name = ${factor_name}, frequency = ${frequency}`);
  conditions.push(
    Sequelize.where(Sequelize.col("bmg_factor_name"), {
      [Op.eq]: `${factor_name}`,
    })
  );
  conditions.push(
    Sequelize.where(Sequelize.col("frequency"), {
      [Op.eq]: `${frequency}`,
    })
  );

  const { limit, offset } = common.getPagination(page, size);

  StockStat.findAndCountAll({
    where: conditions ? conditions : null,
    limit,
    offset,
    order: ["ticker", "from_date"],
  })
    .then((data) => {
      console.log(`stock_stats.controller::findAll -> findAndCountAll = ${data}`);
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
