module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "stock_data",
    {
      ticker: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      date: {
        type: Sequelize.DATE,
        primaryKey: true,
      },
      close: {
        type: Sequelize.DECIMAL(30, 10),
      },
    },
    {
      timestamps: false,
      tableName: "stock_data",
    }
  );
};
