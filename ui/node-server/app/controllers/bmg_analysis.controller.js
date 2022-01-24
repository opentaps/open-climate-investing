const db = require("../models");
const common = require("./common.js");
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
  let sector = null;
  let sortDir = 'ASC';
  let sort = req.query['sort'] || 'sector';
  if (sort && sort[0] == '-') {
    sort = sort.substring(1);
    sortDir = 'DESC';
  }

  if (req.query["f"]) {
    factors = req.query["f"].split(',');
  }
  if (req.query["t"]) {
    tickers = req.query["t"].split(',');
  }
  if (req.query["s"]) {
    sigma = parseFloat(req.query["s"]);
  }
  if (req.query["sector"]) {
    sector = req.query["sector"];
  }

  const { page, size } = req.query;
  const { limit, offset } = common.getPagination(page, size);
  let frequency = req.query["frequency"];
  if (!frequency) frequency = 'MONTHLY';
  let params = { sigma, frequency, limit, offset };

  // get the count of stock with significant regressions
  let total_sql = 'select COUNT(*) as "count" from ('
  let sql = `select ss.ticker, ss.bmg_factor_name, s.sector, s.name,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) as significant,
        avg(bmg) as avg_bmg,
        avg(bmg_t_stat) as avg_bmg_t_stat,
        min(bmg_t_stat) as min_bmg_t_stat,
        max(bmg_t_stat) as max_bmg_t_stat
        from stock_stats ss
        left join stocks s on ss.ticker = s.ticker
        where s.sector is not null and s.sector != '' and ss.frequency = :frequency `;
  if (factors && factors.length) {
    sql += ' and bmg_factor_name IN (:factors) ';
    params.factors = factors;
  }
  if (tickers && tickers.length) {
    sql += ' and ss.ticker IN (:tickers) ';
    params.tickers = tickers;
  }
  if (sector) {
    sql += ' and s.sector = :sector ';
    params.sector = sector;
  }
  sql += `
        group by ss.ticker, ss.bmg_factor_name, s.sector, s.name
        having count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) > count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END)
        `;
  // add sort, validate the given field
  if (sort === 'sector') {
    sql += ` order by s.sector ${sortDir}, ss.ticker`;
  } else if (sort === 'ticker') {
    sql += ` order by ss.ticker ${sortDir}`;
  } else if (sort === 'name') {
    sql += ` order by s.name ${sortDir}`;
  } else if (sort === 'total') {
    sql += ` order by total ${sortDir}`;
  } else if (sort === 'avg_bmg') {
    sql += ` order by avg_bmg ${sortDir}`;
  } else if (sort === 'avg_bmg_t_stat') {
    sql += ` order by avg_bmg_t_stat ${sortDir}`;
  } else if (sort === 'min_bmg_t_stat') {
    sql += ` order by min_bmg_t_stat ${sortDir}`;
  } else if (sort === 'max_bmg_t_stat') {
    sql += ` order by max_bmg_t_stat ${sortDir}`;
  } else {
    sql += ' order by s.sector, ss.ticker';
  }

  let end_total_sql = `) x;`;
  let end_query_sql = ` limit :limit offset :offset;`;

  db.sequelize.query(
    total_sql + sql + end_total_sql,
    {
      replacements: params,
      type: Sequelize.QueryTypes.SELECT,
      raw: true
    })
    .then((count_data) => {
      console.log('stocksWithSignificantRegressions COUNT = ', count_data);
      db.sequelize.query(
        sql + end_query_sql,
        {
          replacements: params,
          type: Sequelize.QueryTypes.SELECT,
          raw: true
        })
        .then((data) => {
          console.log(`stocksWithSignificantRegressions RESULT = ${data}`);
          res.send(common.getPagingData({rows: data, count: parseInt(count_data && count_data[0] ? count_data[0].count : 0)}, page, limit));
        })
        .catch((err) => {
          console.error('stocksWithSignificantRegressions ERROR: ', err);
          res.status(500).send({
            message:
            err.message || "Some error occurred while retrieving the data.",
          });
        });
    })
    .catch((err) => {
      console.error('stocksWithSignificantRegressions ERROR: ', err);
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
  let frequency = req.query["frequency"];
  if (!frequency) frequency = 'MONTHLY';
  let params = { sigma, frequency };

  // get the count of sectors with significant regressions
  let sql = `select sector, bmg_factor_name, count(ticker)
        from (select ss.ticker, ss.bmg_factor_name, s.sector,
        count(1) as total,
        count(CASE WHEN bmg_p_gt_abs_t >= :sigma THEN 1 END) as not_significant,
        count(CASE WHEN bmg_p_gt_abs_t < :sigma THEN 1 END) as significant
        from stock_stats ss
        left join stocks s on s.ticker = ss.ticker
        where s.sector is not null and s.sector != '' and ss.frequency = :frequency `;
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
      console.error('sectorsWithSignificantRegressions ERROR: ', err);
      res.status(500).send({
        message:
        err.message || "Some error occurred while retrieving the data.",
      });
    });
};



