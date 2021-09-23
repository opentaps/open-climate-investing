module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "stock",
    {
      ticker: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      name: Sequelize.STRING,
      sector: Sequelize.STRING,
      sub_sector: Sequelize.STRING,
    },
    {
      timestamps: false,
      tableName: "stocks",
    }
  );
};
