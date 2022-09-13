const db = require("../models");
const common = require("./common.js");
const StockStat = db.stock_stat;
const Sequelize = db.Sequelize;
const Op = db.Sequelize.Op;

exports.findFrequencies = (req, res) => {
  let conditions = [];
  let attributes = [];
  if (req.query["ticker"]) {
    conditions.push(
      Sequelize.where(Sequelize.col("ticker"), {
        [Op.eq]: `${req.query["ticker"]}`,
      })
    );
    attributes.push([
      Sequelize.fn("DISTINCT", Sequelize.col("frequency"), Sequelize.col("interval")),
      "frequency",
    ]);
    StockStat.findAll({
      where: conditions ? conditions : null,
      attributes
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
  } else {
    const sql = `WITH RECURSIVE t AS (
      (SELECT frequency FROM stock_stats ORDER BY frequency LIMIT 1)
      UNION ALL
      SELECT (SELECT frequency FROM stock_stats WHERE frequency > t.frequency ORDER BY frequency LIMIT 1)
      FROM t
      WHERE t.frequency IS NOT NULL
      )
      SELECT frequency AS factor_name FROM t WHERE frequency IS NOT NULL;
      `;
    db.sequelize.query(
      sql,
      {
        type: Sequelize.QueryTypes.SELECT,
        raw: true
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
  }
};

exports.findFactorNames = (req, res) => {
  let sql = '';
  let params = {};
  if (req.query["ticker"]) {
    params.ticker = req.query["ticker"];
    sql = `WITH RECURSIVE t AS (
      (SELECT bmg_factor_name FROM stock_stats WHERE ticker := ticker ORDER BY bmg_factor_name LIMIT 1)
      UNION ALL
      SELECT (SELECT bmg_factor_name FROM stock_stats WHERE ticker := ticker AND bmg_factor_name > t.bmg_factor_name ORDER BY bmg_factor_name LIMIT 1)
      FROM t
      WHERE t.bmg_factor_name IS NOT NULL
      )
      SELECT bmg_factor_name AS factor_name FROM t WHERE bmg_factor_name IS NOT NULL;
      `;
  } else {
    sql = `WITH RECURSIVE t AS (
      (SELECT bmg_factor_name FROM stock_stats ORDER BY bmg_factor_name LIMIT 1)
      UNION ALL
      SELECT (SELECT bmg_factor_name FROM stock_stats WHERE bmg_factor_name > t.bmg_factor_name ORDER BY bmg_factor_name LIMIT 1)
      FROM t
      WHERE t.bmg_factor_name IS NOT NULL
      )
      SELECT bmg_factor_name AS factor_name FROM t WHERE bmg_factor_name IS NOT NULL;
      `;

  }
  db.sequelize.query(
    sql,
    {
      replacements: params,
      type: Sequelize.QueryTypes.SELECT,
      raw: true
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
  let interval = undefined;
  // if frequency is a tuple like (DAILY,90) then split it into frequency and interval
  if (frequency.startsWith('(')) {
    let parts = frequency.substring(1, frequency.length-1).split(',');
    frequency = parts[0];
    interval = parts[1];
  }
  console.log(`stock_stats.controller::findAll -> factor_name = ${factor_name}, frequency = ${frequency}, interval = ${interval}`);
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
  if (interval) {
    conditions.push(
      Sequelize.where(Sequelize.col("interval"), {
        [Op.eq]: `${interval}`,
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
