const db = require("../models");
const common = require("./common.js");
const Stock = db.stock;
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
    let cond = _makeCondition(k, null, req.query[k]);
    if (cond) {
      if (cond.model) {
        let key = cond.alias ? cond.alias : cond.model.name;
        let assocConditions = assocConditionsMap[key];
        if (!assocConditions) {
          assocConditions = [];
          modelsMap[key] = cond.model;
        }
        console.log("findAll -> adding assocConditions", cond.model, cond.cond);
        assocConditionsMap[key] = assocConditions.concat(cond.cond);
      } else {
        console.log("findAll -> adding conditions", cond);
        conditions = conditions.concat(cond);
      }
    }
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
    console.log("findAll -> add include query for ", model, assocConditions);
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
  query.order = ["ticker"];
  console.log("findAll -> query", query);

  Stock.findAndCountAll(query)
    .then((data) => {
      console.log(`findAll -> findAndCountAll = ${data}`);
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

  Stock.findByPk(id)
    .then((data) => {
      res.send(data);
    })
    .catch((err) => {
      res.status(500).send({
        message: "Error retrieving Stock with id=" + id,
      });
    });
};
