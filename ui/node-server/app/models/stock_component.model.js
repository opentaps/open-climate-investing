module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "stock_component",
    {
      ticker: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      component_stock: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      percentage: {
        type: Sequelize.DECIMAL(8, 5),
      },
    },
    {
      timestamps: false,
      tableName: "stock_components",
    }
  );
};
