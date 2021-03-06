import http from "../http-common";

class StockDataService {
  getAll(params) {
    return http.get("/stocks", { params });
  }

  get(id, params) {
    return http.get(`/stocks/${id}`, { params });
  }

  getData(params) {
    return http.get("/data", { params });
  }

  getFrequencies(params) {
    return http.get("/frequencies", { params });
  }

  getFactorNames(params) {
    return http.get("/factor_names", { params });
  }

  getStats(params) {
    return http.get("/stats", { params });
  }

  getComponents(id, params) {
    return http.get(`/stock_components/${id}`, { params });
  }

  getParents(id, params) {
    return http.get(`/stock_parents/${id}`, { params });
  }

  getBmgAnalysisBaseCount(params) {
    return http.get(`/bmg_analysis/count`, { params });
  }

  getStocksBmgAnalysis(params) {
    return http.get(`/bmg_analysis/stocks`, { params });
  }

  getSectorsBmgAnalysis(params) {
    return http.get(`/bmg_analysis/sectors`, { params });
  }

  getColoringClassForStat(p_gt_abs_t) {
    if (p_gt_abs_t === undefined) {
      return "";
    }
    if (p_gt_abs_t < 0.05) {
      return "stat_005";
    } else if (p_gt_abs_t < 0.1) {
      return "stat_01";
    }
    return "stat_other";
  }

  fields() {
    return [
      { label: "Ticker", name: "ticker", searchOnly: true },
      { label: "Name", name: "name", searchOnly: true },
      { label: "Sector", name: "sector" },
      { label: "Sub Sector", name: "sub_sector" },
      { label: "BMG", name: "bmg" },
      { label: "Market", name: "mkt_rf" },
      { label: "SMB", name: "smb" },
      { label: "HML", name: "hml" },
      { label: "WML", name: "wml" },
      { label: "R Squared", name: "r_squared" },
    ];
  }

  stock_data_fields() {
    return [
      { label: "Ticker", name: "ticker", searchOnly: true },
      { label: "Date", name: "date", fmtDate: true },
      { label: "Price", name: "close" },
      { label: "Return", name: "return" },
    ];
  }

  stock_stats_fields() {
    return [
      { label: "Ticker", name: "ticker", searchOnly: true },
      { label: "From Date", name: "from_date", fmtDate: true },
      { label: "Thru Date", name: "thru_date", fmtDate: true },
      { label: "Constant", name: "constant" },
      {
        label: "Constant Std Error",
        name: "constant_std_error",
        fmtNumber: true,
      },
      { label: "Constant T Stat", name: "constant_t_stat" },
      { label: "Constant P>|t|", name: "constant_p_gt_abs_t" },
      { label: "BMG", name: "bmg" },
      { label: "BMG Std Error", name: "bmg_std_error" },
      { label: "BMG T Stat", name: "bmg_t_stat" },
      { label: "BMG P>|t|", name: "bmg_p_gt_abs_t" },
      { label: "Market RF", name: "mkt_rf" },
      {
        label: "Market RF Std Error",
        name: "mkt_rf_std_error",
        fmtNumber: true,
      },
      { label: "Market RF T Stat", name: "mkt_rf_t_stat" },
      { label: "Market RF P>|t|", name: "mkt_rf_p_gt_abs_t" },
      { label: "SMB", name: "smb" },
      { label: "SMB Std Error", name: "smb_std_error" },
      { label: "SMB T Stat", name: "smb_t_stat" },
      { label: "SMB P>|t|", name: "smb_p_gt_abs_t" },
      { label: "HML", name: "hml" },
      { label: "HML Std Error", name: "hml_std_error" },
      { label: "HML T Stat", name: "hml_t_stat" },
      { label: "HML P>|t|", name: "hml_p_gt_abs_t" },
      { label: "WML", name: "wml" },
      { label: "WML Std Error", name: "wml_std_error" },
      { label: "WML T Stat", name: "wml_t_stat" },
      { label: "WML P>|t|", name: "wml_p_gt_abs_t" },
      { label: "Jarque Bera", name: "jarque_bera" },
      {
        label: "Jarque Bera P>|t|",
        name: "jarque_bera_p_gt_abs_t",
        fmtNumber: true,
      },
      { label: "Breusch Pagan", name: "breusch_pagan" },
      {
        label: "Breusch Pagan P>|t|",
        name: "breusch_pagan_p_gt_abs_t",
        fmtNumber: true,
      },
      { label: "Durbin Watson", name: "durbin_watson" },
      { label: "R Squared", name: "r_squared" },
    ];
  }

  stock_comp_fields() {
    return [
      { label: "Ticker", name: "ticker" },
      { label: "Percentage", name: "percentage" },
      { label: "Name", name: "name", searchOnly: true },
      { label: "Sector", name: "sector", searchOnly: true },
      { label: "Sub Sector", name: "sub_sector", searchOnly: true },
      { label: "BMG", name: "bmg" },
      { label: "Market", name: "mkt_rf" },
      { label: "SMB", name: "smb" },
      { label: "HML", name: "hml" },
      { label: "WML", name: "wml" },
      { label: "R Squared", name: "r_squared" },
    ];
  }
}

export default new StockDataService();
