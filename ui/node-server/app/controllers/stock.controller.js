const db = require("../models");
const common = require("./common.js");
const Stock = db.stock_and_stat;
const StockOnly = db.stock;
const StockComponent = db.stock_component_and_stat;
const StockParent = db.stock_parent_and_stat;
const Sequelize = db.Sequelize;
const Op = db.Sequelize.Op;

const _makeCol = (field, alias) => {
  return alias ? Sequelize.col(`${alias}.${field}`) : Sequelize.col(field);
};

const _makeCaseInsensitiveCond = (fieldType, field, op, value, assocAlias) => {
  if ("STRING" === fieldType) {
    return Sequelize.where(Sequelize.fn("lower", _makeCol(field, assocAlias)), {
      [op]: `${value.toLowerCase()}`,
    });
  }
  return Sequelize.where(_makeCol(field, assocAlias), { [op]: `${value}` });
};

const _makeCondition = (field, op, value, alias) => {
  if (!field || !value) {
    console.log("_makeCondition missing field or value: ", field, value);
    return null;
  }
  if (!op) {
    // check if we parsed the field yet
    let idx = field.indexOf("__");
    if (idx > 0) {
      op = field.substring(idx + 2);
      field = field.substring(0, idx);
      return _makeCondition(field, op, value);
    }
    // else default to contains
    return _makeCondition(field, "contains", value);
  }

  let fieldType;
  let actualField = field;
  let modelField = null;
  let assocModel = null;
  let extraCond = null;
  // field must be in the model
  modelField = Stock.rawAttributes[field];
  if (!modelField) {
    console.log("_makeCondition ignoring unknown field: ", field);
    return null;
  }
  fieldType = modelField.type.key;

  return _makeConditionInternal(
    actualField,
    fieldType,
    op,
    value,
    assocModel,
    alias,
    extraCond
  );
};

const _makeConditionInternal = (
  field,
  fieldType,
  op,
  value,
  assocModel,
  assocAlias,
  extraCond
) => {
  // for assocModel we need to wrap the where condition in an include for that model
  let cond = _makeConditionInternal2(field, fieldType, op, value, assocAlias);
  if (extraCond) {
    if (extraCond.model) {
      cond = [cond, extraCond.cond];
    } else {
      cond = [cond, extraCond];
    }
  }
  if (assocModel) {
    return {
      model: assocModel,
      alias: assocAlias,
      cond,
    };
  }
  return cond;
};

const _makeConditionInternal2 = (field, fieldType, op, value, assocAlias) => {
  if (op === "contains") {
    return Sequelize.where(Sequelize.fn("lower", _makeCol(field, assocAlias)), {
      [Op.like]: `%${value.toLowerCase()}%`,
    });
  } else if (op == "eq") {
    return _makeCaseInsensitiveCond(fieldType, field, Op.eq, value, assocAlias);
  } else if (op == "neq") {
    return _makeCaseInsensitiveCond(fieldType, field, Op.ne, value, assocAlias);
  } else if (op == "gte") {
    return _makeCaseInsensitiveCond(
      fieldType,
      field,
      Op.gte,
      value,
      assocAlias
    );
  } else if (op == "gt") {
    return _makeCaseInsensitiveCond(fieldType, field, Op.gt, value, assocAlias);
  } else if (op == "lte") {
    return _makeCaseInsensitiveCond(
      fieldType,
      field,
      Op.lte,
      value,
      assocAlias
    );
  } else if (op == "lt") {
    return _makeCaseInsensitiveCond(fieldType, field, Op.lt, value, assocAlias);
  } else {
    console.log("_makeCondition ignoring unknown operator: ", op);
    return null;
  }
};

// Retrieve all from the database.
// Applies the filters as given in the request
exports.findAll = (req, res) => {
  const { page, size } = req.query;

  let conditions = [];
  // Note: use an modelsMap to map from the model name to the model instance
  // since we can only use model Name as a Key
  // but we need the instance later in the query
  let modelsMap = {};
  let assocConditionsMap = {};
  for (let k in req.query) {
    // ignore factor_name and frequency handled below
    if ('frequency' === k || 'factorName' === k || 'factor_name' === k || 'bmg_factor_name' === k) continue;
    let cond = _makeCondition(k, null, req.query[k]);
    if (cond) {
      if (cond.model) {
        let key = cond.alias ? cond.alias : cond.model.name;
        let assocConditions = assocConditionsMap[key];
        if (!assocConditions) {
          assocConditions = [];
          modelsMap[key] = cond.model;
        }
        console.log("stock.controller::findAll -> adding assocConditions", cond.model, cond.cond);
        assocConditionsMap[key] = assocConditions.concat(cond.cond);
      } else {
        console.log("stock.controller::findAll -> adding conditions", cond);
        conditions = conditions.concat(cond);
      }
    }
  }
  // always filter the factor_name
  let factor_name = req.query["factorName"] || req.query["factor_name"] || req.query["bmg_factor_name"] || "DEFAULT";
  let frequency = req.query["frequency"] || 'MONTHLY';
  let interval = undefined;
  // if frequency is a tuple like (DAILY,90) then split it into frequency and interval
  if (frequency.startsWith('(')) {
    let parts = frequency.substring(1, frequency.length-1).split(',');
    frequency = parts[0];
    interval = parts[1];
  }
  console.log(`stock.controller::findAll -> factor_name = ${factor_name}, frequency = ${frequency} interval = ${interval}`);
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

  let query = {
    limit,
    offset,
  };
  if (conditions) {
    query.where = conditions;
  }
  let includes = [];
  for (let model in assocConditionsMap) {
    let assocConditions = assocConditionsMap[model];
    console.log("stock.controller::findAll -> add include query for ", model, assocConditions);
    let includeCondition = {
      model: modelsMap[model],
      attributes: [],
      where: assocConditions,
      required: true,
    };
    if (modelsMap[model].name !== model) {
      includeCondition.as = model;
    }
    includes.push(includeCondition);
  }
  if (includes.length) {
    query.include = includes;
    query.subQuery = false;
  }
  let sort = req.query['sort'] || 'ticker';
  if (sort && sort[0] == '-') {
    sort = [sort.substring(1), 'DESC'];
  }
  query.order = [sort];
  console.log("stock.controller::findAll -> query", query);

  Stock.findAndCountAll(query)
    .then((data) => {
      console.log(`stock.controller::findAll -> findAndCountAll = ${data}`);
      const response = common.getPagingData(data, page, limit);
      res.send(response);
    })
    .catch((err) => {
      res.status(500).send({
        message: err.message || "Some error occurred while retrieving stocks.",
      });
    });
};

// Find a single with an id
exports.findOne = (req, res) => {
  const id = req.params.id;
  let factor_name = req.query["factorName"] || req.query["factor_name"] || req.query["bmg_factor_name"] || "DEFAULT";
  let frequency = req.query["frequency"] || 'MONTHLY';
  let interval = undefined;
  // if frequency is a tuple like (DAILY,90) then split it into frequency and interval
  if (frequency.startsWith('(')) {
    let parts = frequency.substring(1, frequency.length-1).split(',');
    frequency = parts[0];
    interval = parts[1];
  }
  let conditions = [];
  console.log(`stock.controller::findOne id [${id}] -> factor_name = ${factor_name}, frequency = ${frequency} interval = ${interval}`);
  conditions.push(
    Sequelize.where(Sequelize.col("ticker"), {
      [Op.eq]: `${id}`,
    })
  );
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

  Stock.findOne({where: conditions})
    .then((data) => {
      if (data) res.send(data);
      else {
        StockOnly.findByPk(id)
          .then((data)=>res.send(data))
          .catch((err) => {
            console.error('stock.controller::findOne error: ', err);
            res.status(500).send({
              message: "Error retrieving Stock with id=" + id,
            });
          });
      }
    })
    .catch((err) => {
      console.error('stock.controller::findOne error: ', err);
      res.status(500).send({
        message: "Error retrieving Stock with id=" + id,
      });
    });
};

// Find stocks components with :id parameter as the parent ticker
exports.findComponents = (req, res) => {
  const id = req.params.id;
  const { page, size } = req.query;
  const { limit, offset } = common.getPagination(page, size);

  let query = {
    limit,
    offset,
  };

  let conditions = [];
  conditions.push(Sequelize.where(Sequelize.col("parent_ticker"), { [Op.eq]: id }));
  let factor_name = req.query["factorName"] || req.query["factor_name"] || req.query["bmg_factor_name"] || "DEFAULT";
  let frequency = req.query["frequency"] || 'MONTHLY';
  let interval = undefined;
  // if frequency is a tuple like (DAILY,90) then split it into frequency and interval
  if (frequency.startsWith('(')) {
    let parts = frequency.substring(1, frequency.length-1).split(',');
    frequency = parts[0];
    interval = parts[1];
  }
  console.log(`stock.controller::findComponents -> factor_name = ${factor_name}, frequency = ${frequency} interval = ${interval}`);
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

  query.where = conditions;
  query.order = [["percentage", "DESC"], "ticker"];
  console.log("stock.controller::findComponents -> query", query);

  StockComponent.findAndCountAll(query)
    .then((data) => {
      console.log(`stock.controller::findComponents -> findAndCountAll = ${data}`);
      const response = common.getPagingData(data, page, limit);
      res.send(response);
    })
    .catch((err) => {
      console.log(err);
      res.status(500).send({
        message:
          err.message ||
          "Some error occurred while retrieving stock components.",
      });
    });
};

// Find stocks parents with :id parameter as the component ticker
exports.findParents = (req, res) => {
  const id = req.params.id;
  const { page, size } = req.query;
  const { limit, offset } = common.getPagination(page, size);

  let query = {
    limit,
    offset,
  };

  let conditions = [];
  conditions.push(Sequelize.where(Sequelize.col("component_stock"), { [Op.eq]: id }));
  let factor_name = req.query["factorName"] || req.query["factor_name"] || req.query["bmg_factor_name"] || "DEFAULT";
  let frequency = req.query["frequency"] || 'MONTHLY';
  let interval = undefined;
  // if frequency is a tuple like (DAILY,90) then split it into frequency and interval
  if (frequency.startsWith('(')) {
    let parts = frequency.substring(1, frequency.length-1).split(',');
    frequency = parts[0];
    interval = parts[1];
  }
  console.log(`stock.controller::findParents -> factor_name = ${factor_name}, frequency = ${frequency} interval = ${interval}`);
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

  query.where = conditions;
  query.order = [["percentage", "DESC"], "ticker"];
  console.log("stock.controller::findParents -> query", query);

  StockParent.findAndCountAll(query)
    .then((data) => {
      console.log(`stock.controller::findParents -> findAndCountAll = ${data}`);
      const response = common.getPagingData(data, page, limit);
      res.send(response);
    })
    .catch((err) => {
      console.log(err);
      res.status(500).send({
        message:
          err.message || "Some error occurred while retrieving stock parents.",
      });
    });
};
