const db = require("../models");
const Sequelize = db.Sequelize;

exports.countStocksPerSector = (req, res) => {
  let ticker = null;

  if (req.query["t"]) {
    ticker = req.query["t"];
  }
  if (!ticker) return res.status(500).send({message: 'Ticker parameter t is required'});

  let params = { ticker };

  // get the count of stock per sector for the given composite stock ticker
  let sql = `select distinct S.sector, count(SC.component_stock)
        from stocks as S
        join stock_components as SC
        on S.ticker = SC.component_stock
        where SC.ticker = :ticker
        group by S.sector
        order by S.sector;`;

  db.sequelize.query(
    sql,
    {
      replacements: params,
      type: Sequelize.QueryTypes.SELECT,
      raw: true
    })
    .then((data) => {
      console.log(`countStocksPerSector = ${data}`);
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message:
        err.message || "Some error occurred while retrieving the data.",
      });
    });
};


exports.stocksWithSignificantRegressions = (req, res) => {
  let sigma = 0.05;
  let factors = null;
  let tickers = null;

  if (req.query["f"]) {
    factors = req.query["f"].split(',');
  }
  if (req.query["t"]) {
    tickers = req.query["t"].split(',');
  }
  if (req.query["s"]) {
    sigma = parseFloat(req.query["s"]);
  }
  let params = { sigma };

  // get the count of stock with significant regressions
  let sql = `select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on ss.ticker = s.ticker
        where s.sector is not null and s.sector != '' `;
  if (factors && factors.length) {
    sql += ' and bmg_factor_name IN (:factors) ';
    params.factors = factors;
  }
  if (tickers && tickers.length) {
    sql += ' and ss.ticker IN (:tickers) ';
    params.tickers = tickers;
  }

  sql += ` group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END);`;

  db.sequelize.query(
    sql,
    {
      replacements: params,
      type: Sequelize.QueryTypes.SELECT,
      raw: true
    })
    .then((data) => {
      console.log(`stocksWithSignificantRegressions = ${data}`);
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message:
        err.message || "Some error occurred while retrieving the data.",
      });
    });
};

exports.sectorsWithSignificantRegressions = (req, res) => {
  let sigma = 0.05;
  let factors = null;

  if (req.query["f"]) {
    factors = req.query["f"].split(',');
  }
  if (req.query["s"]) {
    sigma = parseFloat(req.query["s"]);
  }
  let params = { sigma };

  // get the count of sectors with significant regressions
  let sql = `select sector, bmg_factor_name, count(ticker)
        from (select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on s.ticker = ss.ticker
        where s.sector is not null and s.sector != '' `;
  if (factors && factors.length) {
    sql += ' and bmg_factor_name = :factors ';
    params.factors = factors;
  }

  sql += ` group by ss.ticker, ss.bmg_factor_name, s.sector
        having count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END)) x
        group by sector, bmg_factor_name
        order by count(ticker) desc, sector;`;

  db.sequelize.query(
    sql,
    {
      replacements: params,
      type: Sequelize.QueryTypes.SELECT,
      raw: true
    })
    .then((data) => {
      console.log(`sectorsWithSignificantRegressions = ${data}`);
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message:
        err.message || "Some error occurred while retrieving the data.",
      });
    });
};



