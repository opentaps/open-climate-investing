module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "ff_factor",
    {
      date: {
        type: Sequelize.DATE,
        primaryKey: true,
      },
      frequency: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      mkt_rf: Sequelize.DECIMAL(8, 5),
      smb: Sequelize.DECIMAL(8, 5),
      hml: Sequelize.DECIMAL(8, 5),
      wml: Sequelize.DECIMAL(8, 5),
    },
    {
      timestamps: false,
      tableName: "ff_factor",
    }
  );
};
