import http from "../http-common";

class StockDataService {
  getAll(params) {
    return http.get("/stocks", { params });
  }

  get(id) {
    return http.get(`/stocks/${id}`);
  }

  getData(params) {
    return http.get("/data", { params });
  }

  getStats(params) {
    return http.get("/stats", { params });
  }

  fields() {
    return [
      { label: "Ticker", name: "ticker" },
      { label: "Name", name: "name" },
      { label: "Sector", name: "sector" },
      { label: "Sub Sector", name: "sub_sector" },
    ];
  }

  stock_data_fields() {
    return [
      { label: "Ticker", name: "ticker" },
      { label: "Date", name: "date", fmtDate: true },
      { label: "Close", name: "close" },
    ];
  }

  stock_stats_fields() {
    return [
      { label: "Ticker", name: "ticker" },
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
}

export default new StockDataService();
