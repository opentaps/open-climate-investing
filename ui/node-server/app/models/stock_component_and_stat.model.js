module.exports = (sequelize, Sequelize) => {
  return sequelize.define(
    "stock_component_and_stat",
    {
      ticker: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      parent_ticker: {
        type: Sequelize.STRING,
        primaryKey: true,
      },
      percentage: {
        type: Sequelize.DECIMAL(8, 5),
      },
      name: Sequelize.STRING,
      sector: Sequelize.STRING,
      sub_sector: Sequelize.STRING,
      from_date: {
        type: Sequelize.DATE,
        primaryKey: true,
      },
      thru_date: {
        type: Sequelize.DATE,
        primaryKey: true,
      },
      constant: Sequelize.DECIMAL(12, 5),
      constant_std_error: Sequelize.DECIMAL(12, 5),
      constant_t_stat: Sequelize.DECIMAL(12, 5),
      constant_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      bmg: Sequelize.DECIMAL(12, 5),
      bmg_std_error: Sequelize.DECIMAL(12, 5),
      bmg_t_stat: Sequelize.DECIMAL(12, 5),
      bmg_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      mkt_rf: Sequelize.DECIMAL(12, 5),
      mkt_rf_std_error: Sequelize.DECIMAL(12, 5),
      mkt_rf_t_stat: Sequelize.DECIMAL(12, 5),
      mkt_rf_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      smb: Sequelize.DECIMAL(12, 5),
      smb_std_error: Sequelize.DECIMAL(12, 5),
      smb_t_stat: Sequelize.DECIMAL(12, 5),
      smb_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      hml: Sequelize.DECIMAL(12, 5),
      hml_std_error: Sequelize.DECIMAL(12, 5),
      hml_t_stat: Sequelize.DECIMAL(12, 5),
      hml_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      wml: Sequelize.DECIMAL(12, 5),
      wml_std_error: Sequelize.DECIMAL(12, 5),
      wml_t_stat: Sequelize.DECIMAL(12, 5),
      wml_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      jarque_bera: Sequelize.DECIMAL(12, 5),
      jarque_bera_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      breusch_pagan: Sequelize.DECIMAL(12, 5),
      breusch_pagan_p_gt_abs_t: Sequelize.DECIMAL(12, 5),
      durbin_watson: Sequelize.DECIMAL(12, 5),
      r_squared: Sequelize.DECIMAL(12, 5),
    },
    {
      timestamps: false,
      tableName: "stock_component_and_stats",
    }
  );
};
