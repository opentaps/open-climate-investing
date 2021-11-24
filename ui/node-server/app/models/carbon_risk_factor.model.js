module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "carbon_risk_factor",
    {
      date: {
        type: Sequelize.DATE,
        primaryKey: true,
      },
      factor_name: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      bmg: Sequelize.DECIMAL(12, 10),
    },
    {
      timestamps: false,
      tableName: "carbon_risk_factors",
    }
  );
};
