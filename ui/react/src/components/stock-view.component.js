import CircularProgress from "@mui/material/CircularProgress";
import Pagination from "@mui/material/Pagination";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import React, { Component } from "react";
import Chart from "react-apexcharts";
import Linkify from "react-linkify";
import StockDataService from "../services/stock.service";

const componentDecorator = (href, text, key) => (
  <a href={href} key={key} target="_blank" rel="noreferrer">
    {text}
  </a>
);

const STAT_TABLE_FIELDS = [
  { label: "Carbon", name: "bmg" },
  { label: "Market", name: "mkt_rf" },
  { label: "SMB", name: "smb" },
  { label: "HML", name: "hml" },
  { label: "WML", name: "wml" },
];

const STAT_BOX_FIELDS = [
  { label: "R2", name: "r_squared" },
  { label: "Jarque-Bera", name: "jarque_bera" },
  { label: "Breusch-Pagan", name: "breusch_pagan" },
  { label: "Durbin-Watson", name: "durbin_watson" },
];

// should the graphs be limited to the common date range?
const LIMIT_GRAPHS_DATES = true;
const DEFAULT_PAGE_SIZE = 25;
const DEFAULT_TAB = 0;
const GRAPH_OPTIONS = {
  chart: {
    type: "area",
    stacked: false,
    height: 350,
    zoom: {
      type: "x",
      enabled: true,
      autoScaleYaxis: true,
    },
    toolbar: {
      autoSelected: "zoom",
    },
    animations: {
      enabled: false,
      dynamicAnimation: {
        enabled: false,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  markers: {
    size: 0,
  },
  fill: {
    type: "gradient",
    gradient: {
      shadeIntensity: 1,
      inverseColors: false,
      opacityFrom: 0.5,
      opacityTo: 0,
      stops: [0, 90, 100],
    },
  },
  yaxis: {
    labels: {
      formatter: function (val) {
        return val.toFixed(3);
      },
    },
    title: {
      text: "",
    },
  },
  xaxis: {
    type: "datetime",
  },
  tooltip: {
    shared: false,
    x: {
      format: "yyyy dd MMM",
    },
    y: {
      formatter: function (val) {
        return val;
      },
    },
  },
};

export default class Stock extends Component {
  constructor(props) {
    super(props);
    this.getStock = this.getStock.bind(this);
    this.goBack = this.goBack.bind(this);
    this.retrieveStockGraph = this.retrieveStockGraph.bind(this);
    this.handleTabChange = this.handleTabChange.bind(this);
    this.handleDataPageChange = this.handleDataPageChange.bind(this);
    this.handleDataPageSizeChange = this.handleDataPageSizeChange.bind(this);
    this.handleStatsPageChange = this.handleStatsPageChange.bind(this);
    this.handleStatsPageSizeChange = this.handleStatsPageSizeChange.bind(this);
    this.handleCurrentSeriesChange = this.handleCurrentSeriesChange.bind(this);

    this.pageSizes = [10, 25, 50, 100];
    let stock_graph_options = Object.assign({}, GRAPH_OPTIONS);
    this.state = {
      current_tab: DEFAULT_TAB,
      current: {
        ticker: null,
        name: "",
      },
      message: "",
      data: [],
      data_page: 1,
      data_count: 0,
      data_total: 0,
      data_pageSize: DEFAULT_PAGE_SIZE,
      data_loadingIndicator: false,
      stock_graph_options: stock_graph_options,
      stock_graph_current_series_name: "Price",
      stock_graph_series: [],
      stock_graph_loadingIndicator: false,
      latest_stock_stats: {},
      stats: [],
      stats_page: 1,
      stats_count: 0,
      stats_total: 0,
      stats_pageSize: DEFAULT_PAGE_SIZE,
      stats_loadingIndicator: false,
    };
  }

  componentDidMount() {
    this.getStock(this.props.match.params.id);
  }

  goBack() {
    this.props.history.goBack();
  }

  handleTabChange(event, newValue) {
    this.setState({
      current_tab: newValue,
    });
  }

  getStock(id) {
    StockDataService.get(id)
      .then((response) => {
        this.setState({
          current: response.data,
        });
        console.log(response.data);
        window.scrollTo(0, 0);
        this.retrieveData();
        this.retrieveStats();
        this.retrieveStockGraph();
      })
      .catch((e) => {
        console.log(e);
      });
  }

  getRequestParams(stock, page, pageSize) {
    if (!stock || !stock.ticker) {
      return null;
    }

    let params = { ticker: stock.ticker };

    if (page) {
      params["page"] = page - 1;
    }

    if (pageSize) {
      params["size"] = pageSize;
    }

    console.log("getRequestParams:: params", params);
    return params;
  }

  retrieveData() {
    const { current, data_page, data_pageSize } = this.state;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch data for !");
      return;
    }
    StockDataService.getData(
      this.getRequestParams(current, data_page, data_pageSize)
    )
      .then((data_response) => {
        const { items, totalPages, totalItems } = data_response.data;
        this.setState({
          data: items,
          data_count: totalPages,
          data_total: totalItems,
        });
        this.setState({ data_loadingIndicator: false });
      })
      .catch((e) => {
        this.setState({ data_loadingIndicator: false });
        console.log(e);
      });
  }

  handleDataPageChange(event, value) {
    console.log("handleDataPageChange:: ", event, value);
    this.setState(
      {
        data_page: value,
      },
      () => {
        this.retrieveData();
      }
    );
  }

  handleDataPageSizeChange(event) {
    console.log("handleDataPageSizeChange:: ", event);
    this.setState(
      {
        data_pageSize: event.target.value,
        data_page: 1,
      },
      () => {
        this.retrieveData();
      }
    );
  }

  retrieveStockGraph(page, arr) {
    const { current } = this.state;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch data for !");
      return;
    }
    if (!arr) arr = [];
    if (!page) page = 0;
    StockDataService.getData({
      ticker: current.ticker,
      page: page,
      size: 100,
    })
      .then((stats_response) => {
        const { items, totalPages } = stats_response.data;
        arr = arr.concat(items);
        if (page + 1 < totalPages) {
          this.retrieveStockGraph(page + 1, arr);
        } else {
          let priceSeries = {
            name: "Price",
            data: arr.map((d) => [d.date, parseFloat(d.close)]),
          };
          this.setState({
            stock_graph_series: [
              priceSeries,
              {
                name: "Return %",
                data: arr.map((d) => [d.date, parseFloat(d.return) * 100.0]),
              },
            ],
            stock_graph_current_series_name: "Price",
          });
          // now add the other series from Stats
          this.retrieveStatsGraph();
        }
      })
      .catch((e) => {
        this.setState({ stock_graph_loadingIndicator: false });
        console.log(e);
      });
  }

  retrieveStatsGraph(page, arr) {
    const { current } = this.state;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    if (!arr) arr = [];
    if (!page) page = 0;
    StockDataService.getStats({
      ticker: current.ticker,
      page: page,
      size: 100,
    })
      .then((stats_response) => {
        const { items, totalPages } = stats_response.data;
        console.log("retrieveStatsGraph: ", items);
        arr = arr.concat(items);
        if (page + 1 < totalPages) {
          this.retrieveStatsGraph(page + 1, arr);
        } else {
          // get the min / max date range
          let last = arr[arr.length - 1];
          let min_date = arr[0].from_date;
          let max_date = last.from_date;
          let series = this.state.stock_graph_series.map(s=>{
            return {name: s.name, data: s.data.filter(d=>d[0] >= min_date && d[0] <= max_date)}
          });
          this.setState({
            latest_stock_stats: last,
            stock_graph_series: series.concat([
              {
                name: "Carbon",
                data: arr.map((d) => [d.from_date, parseFloat(d.bmg)]),
              },
              {
                name: "Market",
                data: arr.map((d) => [d.from_date, parseFloat(d.mkt_rf)]),
              },
              {
                name: "SMB",
                data: arr.map((d) => [d.from_date, parseFloat(d.smb)]),
              },
              {
                name: "HML",
                data: arr.map((d) => [d.from_date, parseFloat(d.hml)]),
              },
              {
                name: "WML",
                data: arr.map((d) => [d.from_date, parseFloat(d.wml)]),
              },
            ]),
          });
          this.setState({ stock_graph_loadingIndicator: false });
        }
      })
      .catch((e) => {
        this.setState({ stock_graph_loadingIndicator: false });
        console.log(e);
      });
  }

  retrieveStats() {
    const { current, stats_page, stats_pageSize } = this.state;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    StockDataService.getStats(
      this.getRequestParams(current, stats_page, stats_pageSize)
    )
      .then((stats_response) => {
        const { items, totalPages, totalItems } = stats_response.data;
        this.setState({
          stats: items,
          stats_count: totalPages,
          stats_total: totalItems,
        });
        this.setState({ stats_loadingIndicator: false });
      })
      .catch((e) => {
        this.setState({ stats_loadingIndicator: false });
        console.log(e);
      });
  }

  handleStatsPageChange(event, value) {
    console.log("handleStatsPageChange:: ", event, value);
    this.setState(
      {
        stats_page: value,
      },
      () => {
        this.retrieveStats();
      }
    );
  }

  handleStatsPageSizeChange(event) {
    console.log("handleStatsPageSizeChange:: ", event);
    this.setState(
      {
        stats_pageSize: event.target.value,
        stats_page: 1,
      },
      () => {
        this.retrieveStats();
      }
    );
  }

  handleCurrentSeriesChange(event, value) {
    console.log("handleCurrentSeriesChange:: ", event, value);
    this.setState({
      stock_graph_current_series_name: value,
    });
  }

  renderFormattedField(field, item, prefix) {
    let n = field.name;
    if (prefix) n += prefix;
    return item[n] && field.fmtNumber
      ? parseInt(item[n]).toLocaleString()
      : item[n];
  }

  renderField(field, current) {
    return (
      <div key={field.label}>
        <label>
          <strong>{field.label}:</strong>
        </label>{" "}
        {this.renderFormattedField(field, current)}
      </div>
    );
  }

  renderFieldsTableHeaders(fields) {
    return (
      <thead>
        <tr>
          {fields.map((f) => (
            <th key={f.label} scope="col">
              {f.label}
            </th>
          ))}
        </tr>
      </thead>
    );
  }

  renderFieldsTableRow(fields, item, index) {
    return (
      <tr key={index}>
        {fields.map((f) =>
          f.linkify ? (
            <Linkify componentDecorator={componentDecorator}>
              <td>{this.renderFormattedField(f, item)}</td>
            </Linkify>
          ) : (
            <td key={`${index}_${f.label}`}>
              {this.renderFormattedField(f, item)}
            </td>
          )
        )}
      </tr>
    );
  }

  renderFieldsTableBody(fields, items) {
    return (
      <tbody>
        {items &&
          items.map((item, index) =>
            this.renderFieldsTableRow(fields, item, index)
          )}
      </tbody>
    );
  }

  renderFieldsTable(fields, items) {
    return (
      <table className="table">
        {this.renderFieldsTableHeaders(fields)}
        {this.renderFieldsTableBody(fields, items)}
      </table>
    );
  }

  renderStatsFieldsTable(fields, values) {
    return (
      <table className="table">
        <thead>
          <tr>
            <th colSpan={2}>Risk Factors</th>
            <th>t</th>
            <th>P&gt;|t|</th>
          </tr>
        </thead>
        <tbody>
          {fields.map((f, index) => (
            <tr key={index}>
              <th>{f.label}</th>
              <td>{this.renderFormattedField(f, values)}</td>
              <td>{this.renderFormattedField(f, values, "_t_stat")}</td>
              <td>{this.renderFormattedField(f, values, "_p_gt_abs_t")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  renderSpinner(loading) {
    return loading ? (
      <div className="spinner-placeholder">
        <CircularProgress />
      </div>
    ) : (
      ""
    );
  }

  renderPaginator(count, page, pageSize, pageChangeHandler, pageSizeHandler) {
    return count === 0 ? (
      <p>No items found.</p>
    ) : (
      <div className="row">
        <div className="col-auto">
          <Pagination
            className="my-3"
            count={count}
            page={page}
            siblingCount={1}
            boundaryCount={1}
            variant="outlined"
            shape="rounded"
            onChange={pageChangeHandler}
          />
        </div>
        <div className="col-auto my-3 row">
          <label className="col-auto col-form-label" htmlFor="pageSize">
            Items per Page:
          </label>
          <div className="col-auto">
            <select
              id="pageSize"
              className="form-select"
              onChange={pageSizeHandler}
              value={pageSize}
            >
              {this.pageSizes.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    );
  }

  render() {
    const {
      current,
      message,
      current_tab,
      data,
      data_page,
      data_count,
      data_total,
      data_pageSize,
      data_loadingIndicator,
      stock_graph_options,
      stock_graph_series,
      stock_graph_current_series_name,
      stock_graph_loadingIndicator,
      latest_stock_stats,
      stats,
      stats_page,
      stats_count,
      stats_total,
      stats_pageSize,
      stats_loadingIndicator,
    } = this.state;

    return (
      <div>
        {current ? (
          <div>
            <h4>
              {current.ticker} {current.name}{" "}
              <button
                className="btn btn-primary btn-sm ms-4"
                onClick={this.goBack}
              >
                Back
              </button>
            </h4>

            <Tabs
              value={current_tab}
              indicatorColor="primary"
              textColor="primary"
              onChange={this.handleTabChange}
            >
              <Tab label="Details" />
              <Tab label={`Data (${data_total})`} />
              <Tab label={`Stats (${stats_total})`} />
            </Tabs>

            <p>{message}</p>

            <div role="tabpanel" hidden={current_tab !== 0}>
              <div className="mt-4">
                <label>
                  <strong>Sector:</strong>
                </label>{" "}
                {current.sector}
                {current.sub_sector ? ` / ${current.sub_sector}` : ""}
              </div>
            </div>

            <div role="tabpanel" hidden={current_tab !== 1}>
              {this.renderSpinner(data_loadingIndicator)}
              {this.renderFieldsTable(
                StockDataService.stock_data_fields(),
                data
              )}
              {this.renderPaginator(
                data_count,
                data_page,
                data_pageSize,
                this.handleDataPageChange,
                this.handleDataPageSizeChange
              )}
            </div>

            <div role="tabpanel" hidden={current_tab !== 2}>
              {this.renderSpinner(stats_loadingIndicator)}
              {this.renderFieldsTable(
                StockDataService.stock_stats_fields(),
                stats
              )}
              {this.renderPaginator(
                stats_count,
                stats_page,
                stats_pageSize,
                this.handleStatsPageChange,
                this.handleStatsPageSizeChange
              )}
            </div>

            <div className="mt-2 row align-items-start">
              <div class="col">
                {latest_stock_stats
                  ? this.renderStatsFieldsTable(
                      STAT_TABLE_FIELDS,
                      latest_stock_stats
                    )
                  : ""}
              </div>
              <div class="col">
                {latest_stock_stats ? (
                  <table className="table">
                    <thead>
                      <tr>
                        <th colSpan={2}>Statistics</th>
                      </tr>
                    </thead>
                    <tbody>
                      {STAT_BOX_FIELDS.map((f, i) => (
                        <tr key={i}>
                          <th>{f.label}</th>
                          <td>
                            {this.renderFormattedField(f, latest_stock_stats)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  ""
                )}
              </div>
            </div>

            <div className="mt-2">
              {this.renderSpinner(stock_graph_loadingIndicator)}
              {!stock_graph_loadingIndicator ? (
                <>
                  <ToggleButtonGroup
                    color="primary"
                    value={stock_graph_current_series_name}
                    exclusive
                    onChange={this.handleCurrentSeriesChange}
                  >
                    {stock_graph_series.map((s) => (
                      <ToggleButton key={s.name} value={s.name}>
                        {s.name}
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                  {stock_graph_series.map((s) => (
                    <Chart
                      key={s.name}
                      options={stock_graph_options}
                      series={[s]}
                      type="area"
                      width="100%"
                      style={{
                        display:
                          s.name === stock_graph_current_series_name
                            ? "block"
                            : "none",
                      }}
                    />
                  ))}
                </>
              ) : (
                ""
              )}
            </div>
          </div>
        ) : (
          <div>
            <br />
            <p>Please select on a Stock...</p>
          </div>
        )}
      </div>
    );
  }
}
