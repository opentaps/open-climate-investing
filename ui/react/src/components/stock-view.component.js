import PropTypes from 'prop-types';
import React, { Component } from "react";
import Chart from "react-apexcharts";
import Linkify from "react-linkify";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";
import SeriesSettings, { SeriesContext } from "./series-settings.component";
import { CircularProgress, Pagination, Tab, Tabs, ToggleButton, ToggleButtonGroup } from "@mui/material";

const componentDecorator = (href, text, key) => (
  <a href={href} key={key} target="_blank" rel="noreferrer">
    {text}
  </a>
);

const STAT_TABLE_FIELDS = [
  { label: "BMG", name: "bmg" },
  { label: "Market", name: "mkt_rf" },
  { label: "SMB", name: "smb" },
  { label: "HML", name: "hml" },
  { label: "WML", name: "wml" },
];

const STAT_BOX_FIELDS = [
  { label: "R-sq", name: "r_squared" },
  { label: "Jarque-Bera", name: "jarque_bera" },
  { label: "Breusch-Pagan", name: "breusch_pagan" },
  { label: "Durbin-Watson", name: "durbin_watson" },
];

// should the graphs be limited to the common date range?
const LIMIT_GRAPHS_DATES = true;
const DEFAULT_PAGE_SIZE = 25;
const DEFAULT_TAB = 0;
const DEFAULT_GRAPH = "BMG";
const STAT_GRAPHS_MIN = -1;
const STAT_GRAPHS_MAX = 1;
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

class Stock extends Component {

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
    this.handleComponentsPageChange =
      this.handleComponentsPageChange.bind(this);
    this.handleComponentsPageSizeChange =
      this.handleComponentsPageSizeChange.bind(this);
    this.handleParentsPageChange = this.handleParentsPageChange.bind(this);
    this.handleParentsPageSizeChange =
      this.handleParentsPageSizeChange.bind(this);
    this.handleCurrentSeriesChange = this.handleCurrentSeriesChange.bind(this);
    this.onStockComponentClick = this.onStockComponentClick.bind(this);
    this.onStockParentClick = this.onStockParentClick.bind(this);

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
      stock_graph_stats_options: {},
      stock_graph_current_series_name: DEFAULT_GRAPH,
      stock_graph_series: [],
      stock_graph_loadingIndicator: false,
      latest_stock_stats: null,
      stats: [],
      stats_page: 1,
      stats_count: 0,
      stats_total: 0,
      stats_pageSize: DEFAULT_PAGE_SIZE,
      stats_loadingIndicator: false,
      comp: [],
      comp_page: 1,
      comp_count: 0,
      comp_total: 0,
      comp_pageSize: DEFAULT_PAGE_SIZE,
      comp_loadingIndicator: false,
      parents: [],
      parents_page: 1,
      parents_count: 0,
      parents_total: 0,
      parents_pageSize: DEFAULT_PAGE_SIZE,
      parents_loadingIndicator: false,
    };
  }

  componentDidMount() {
    this.getStock(this.props.match.params.id);
    this.prevContext = this.context;
  }

  componentDidUpdate(prevProps) {
    let changed = false;
    let o = prevProps && prevProps.match && prevProps.match.params.id;
    let n = this.props && this.props.match && this.props.match.params.id;
    changed = (o !== n);
    if (this.prevContext.factorName != this.context.factorName || this.prevContext.frequency != this.context.frequency) {
      changed = true;
    }
    if (changed) {
      this.prevContext = this.context;
      this.getStock(this.props.match.params.id);
    }
  }

  goBack() {
    this.props.history.goBack();
  }

  handleTabChange(_event, newValue) {
    this.setState({
      current_tab: newValue,
    });
  }

  getStock(id) {
    const { frequency, factorName } = this.context;
    StockDataService.get(id, { frequency, factorName })
      .then((response) => {
        this.setState({
          current: response.data || { ticker: id },
          current_tab: DEFAULT_TAB,
          message: "",
        });
        console.log('getStock: ', response.data);
        window.scrollTo(0, 0);
        this.retrieveAllStockData();
      })
      .catch((e) => {
        console.log(e);
      });
  }

  retrieveAllStockData() {
    this.retrieveData();
    this.retrieveStats();
    this.retrieveComponents();
    this.retrieveParents();
    this.retrieveStockGraph();
  }

  getRequestParams(stock, page, pageSize, factorName, frequency) {
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

    if (frequency) {
      params["frequency"] = frequency;
    }

    if (factorName) {
      params["factor_name"] = factorName;
    }

    console.log("getRequestParams:: params", params);
    return params;
  }

  async retrieveData() {
    const { current, data_page, data_pageSize } = this.state;
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch data for !");
      return;
    }
    try {
      const data_response = await StockDataService.getData(
        this.getRequestParams(current, data_page, data_pageSize, factorName, frequency)
      );
      const { items, totalPages, totalItems } = data_response.data;
      this.setState({
        data: items,
        data_count: totalPages,
        data_total: totalItems,
      });
      this.setState({ data_loadingIndicator: false });
    } catch (err) {
      this.setState({ data_loadingIndicator: false });
      console.log(err);
    }
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
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch data for !");
      return;
    }
    if (!arr) arr = [];
    if (!page) page = 0;
    StockDataService.getData({
      ticker: current.ticker,
      page,
      size: 100,
      factorName,
      frequency
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
            stock_graph_current_series_name: DEFAULT_GRAPH,
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
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    if (!arr) arr = [];
    if (!page) page = 0;
    StockDataService.getStats({
      ticker: current.ticker,
      page,
      size: 100,
      factorName,
      frequency
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
          if (!last) {
            this.setState({
              stock_graph_loadingIndicator: false,
              message: "No data on record for this Stock.",
              latest_stock_stats: null,
              stock_graph_series: [],
            });
            return;
          }
          let min_date = arr[0].thru_date;
          let max_date = last.thru_date;
          let series = this.state.stock_graph_series;
          if (LIMIT_GRAPHS_DATES) {
            series = series.map((s) => {
              return {
                name: s.name,
                data: s.data.filter(
                  (d) => d[0] >= min_date && d[0] <= max_date
                ),
              };
            });
          }
          let stat_series = [
            {
              name: "BMG",
              data: arr.map((d) => [d.thru_date, parseFloat(d.bmg)]),
            },
            {
              name: "Market",
              data: arr.map((d) => [d.thru_date, parseFloat(d.mkt_rf)]),
            },
            {
              name: "SMB",
              data: arr.map((d) => [d.thru_date, parseFloat(d.smb)]),
            },
            {
              name: "HML",
              data: arr.map((d) => [d.thru_date, parseFloat(d.hml)]),
            },
            {
              name: "WML",
              data: arr.map((d) => [d.thru_date, parseFloat(d.wml)]),
            },
          ];
          // custom options to render graphs
          let stock_graph_stats_options = {};
          stat_series.forEach((s) => {
            // extract the values
            let data = s.data.map((a) => a[1]);
            // get min / max
            let min = Math.min(...data);
            let max = Math.max(...data);
            min = min < STAT_GRAPHS_MIN ? Math.floor(min) : STAT_GRAPHS_MIN;
            max = max > STAT_GRAPHS_MAX ? Math.ceil(max) : STAT_GRAPHS_MAX;
            // get the range as the number of ticks
            let r = Math.max(4, max - min);
            stock_graph_stats_options[s.name] = Object.assign(
              {},
              GRAPH_OPTIONS,
              {
                yaxis: {
                  max: max,
                  min: min,
                  tickAmount: r,
                },
              }
            );
          });

          this.setState({
            stock_graph_loadingIndicator: false,
            latest_stock_stats: last,
            stock_graph_series: series.concat(stat_series),
            stock_graph_stats_options: stock_graph_stats_options,
          });
        }
      })
      .catch((e) => {
        this.setState({ stock_graph_loadingIndicator: false });
        console.log('Could not load stock graph data', e);
      });
  }

  retrieveComponents() {
    const { current, comp_page, comp_pageSize } = this.state;
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    StockDataService.getComponents(
      current.ticker,
      this.getRequestParams(current, comp_page, comp_pageSize, factorName, frequency)
    )
      .then((comp_response) => {
        const { items, totalPages, totalItems } = comp_response.data;
        this.setState({
          comp_loadingIndicator: false,
          comp: items,
          comp_count: totalPages,
          comp_total: totalItems,
        });
      })
      .catch((e) => {
        this.setState({ comp_loadingIndicator: false });
        console.log(e);
      });
  }

  handleComponentsPageChange(event, value) {
    console.log("handleComponentsPageChange:: ", event, value);
    this.setState(
      {
        comp_page: value,
      },
      () => {
        this.retrieveComponents();
      }
    );
  }

  handleComponentsPageSizeChange(event) {
    console.log("handleComponentsPageSizeChange:: ", event);
    this.setState(
      {
        comp_pageSize: event.target.value,
        comp_page: 1,
      },
      () => {
        this.retrieveComponents();
      }
    );
  }

  onStockComponentClick(e) {
    console.log("onStockComponentClick", e);
    if (e && e.target && e.target.attributes["data-index"]) {
      let i = e.target.getAttribute("data-index");
      let item = this.state.comp[i];
      console.log("onStockComponentClick --> ", i, item);
      this.props.history.push(`/stocks/${item.ticker}`);
    }
  }

  retrieveParents() {
    const { current, parents_page, parents_pageSize } = this.state;
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    StockDataService.getParents(
      current.ticker,
      this.getRequestParams(
        current,
        parents_page,
        parents_pageSize,
        factorName,
        frequency
      )
    )
      .then((parents_response) => {
        const { items, totalPages, totalItems } = parents_response.data;
        this.setState({
          parents_loadingIndicator: false,
          parents: items,
          parents_count: totalPages,
          parents_total: totalItems,
        });
      })
      .catch((e) => {
        this.setState({ parents_loadingIndicator: false });
        console.log(e);
      });
  }

  handleParentsPageChange(event, value) {
    console.log("handleParentsPageChange:: ", event, value);
    this.setState(
      {
        parents_page: value,
      },
      () => {
        this.retrieveParents();
      }
    );
  }

  handleParentsPageSizeChange(event) {
    console.log("handleParentsPageSizeChange:: ", event);
    this.setState(
      {
        parents_pageSize: event.target.value,
        parents_page: 1,
      },
      () => {
        this.retrieveParents();
      }
    );
  }

  onStockParentClick(e) {
    console.log("onStockParentClick", e);
    if (e && e.target && e.target.attributes["data-index"]) {
      let i = e.target.getAttribute("data-index");
      let item = this.state.parents[i];
      console.log("onStockParentClick --> ", i, item);
      this.props.history.push(`/stocks/${item.ticker}`);
    }
  }

  retrieveStats() {
    const { current, stats_page, stats_pageSize } = this.state;
    const { frequency, factorName } = this.context;
    if (!current || !current.ticker) {
      console.log("No current stock to fetch stats for !");
      return;
    }
    StockDataService.getStats(
      this.getRequestParams(current, stats_page, stats_pageSize, factorName, frequency)
    )
      .then((stats_response) => {
        const { items, totalPages, totalItems } = stats_response.data;
        this.setState({
          stats_loadingIndicator: false,
          stats: items,
          stats_count: totalPages,
          stats_total: totalItems,
        });
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

  renderFormattedField(field, item, postfix) {
    let n = field.name;
    if (postfix) n += postfix;
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
          {fields
            .filter((f) => !f.searchOnly)
            .map((f) => (
              <th key={f.label} scope="col">
                {f.label}
              </th>
            ))}
        </tr>
      </thead>
    );
  }

  renderFieldsTableRow(fields, item, index, opts) {
    return (
      <tr key={index}>
        {!opts || !opts.skipTicker ? (
          <td data-index={index} onClick={opts ? opts.onRowClick : null}>
            <b>{item.ticker}</b>: {item.name}
          </td>
        ) : null}
        {fields
          .filter(
            (f) => !f.searchOnly && f.name !== "ticker" && f.name !== "name"
          )
          .map((f) =>
            f.linkify ? (
              <Linkify componentDecorator={componentDecorator}>
                <td>{this.renderFormattedField(f, item)}</td>
              </Linkify>
            ) : (
              <td
                key={`${index}_${f.label}`}
                data-index={index}
                onClick={opts ? opts.onRowClick : null}
                className={StockDataService.getColoringClassForStat(
                  item[f.name + "_p_gt_abs_t"]
                )}
              >
                {this.renderFormattedField(f, item)}
              </td>
            )
          )}
      </tr>
    );
  }

  renderFieldsTableBody(fields, items, opts) {
    return (
      <tbody>
        {items ?
          items.map((item, index) =>
            this.renderFieldsTableRow(fields, item, index, opts)
          ) : ''}
      </tbody>
    );
  }

  renderFieldsTable(fields, items, opts) {
    return (
      <table className={`table ${opts ? opts.tableClassName : null}`}>
        {this.renderFieldsTableHeaders(fields, opts)}
        {this.renderFieldsTableBody(fields, items, opts)}
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
              <td
                data-pgtabs={values[f.name + "_p_gt_abs_t"]}
                className={StockDataService.getColoringClassForStat(
                  values[f.name + "_p_gt_abs_t"]
                )}
              >
                {this.renderFormattedField(f, values)}
              </td>
              <td
                data-pgtabs={values[f.name + "_p_gt_abs_t"]}
                className={StockDataService.getColoringClassForStat(
                  values[f.name + "_p_gt_abs_t"]
                )}
              >
                {this.renderFormattedField(f, values, "_t_stat")}
              </td>
              <td
                data-pgtabs={values[f.name + "_p_gt_abs_t"]}
                className={StockDataService.getColoringClassForStat(
                  values[f.name + "_p_gt_abs_t"]
                )}
              >
                {this.renderFormattedField(f, values, "_p_gt_abs_t")}
              </td>
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
      stock_graph_stats_options,
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
      comp,
      comp_page,
      comp_count,
      comp_total,
      comp_pageSize,
      comp_loadingIndicator,
      parents,
      parents_page,
      parents_count,
      parents_total,
      parents_pageSize,
      parents_loadingIndicator,
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

            <SeriesSettings/>
            
            <Tabs
              value={current_tab}
              indicatorColor="primary"
              textColor="primary"
              onChange={this.handleTabChange}
            >
              <Tab label="Details" />
              <Tab label={`Data (${data_total})`} />
              <Tab label={`Stats (${stats_total})`} />
              {comp_total ? <Tab label={`Components (${comp_total})`} /> : ""}
              {parents_total ? (
                <Tab label={`Parents (${parents_total})`} />
              ) : (
                ""
              )}
            </Tabs>

            <div role="tabpanel" hidden={current_tab !== 0}>
              {current.sector && current.sub_sector ? (
                <div className="mt-4">
                  <label>
                    <strong>Sector:</strong>
                  </label>{" "}
                  {current.sector}
                  {current.sub_sector ? ` / ${current.sub_sector}` : ""}
                </div>
              ) : (
                ""
              )}

              {!stock_graph_loadingIndicator && latest_stock_stats ? (
                <div className="mt-2 row align-items-start">
                  <div className="col">
                    {this.renderStatsFieldsTable(
                      STAT_TABLE_FIELDS,
                      latest_stock_stats
                    )}
                  </div>
                  <div className="col">
                    <table className="table">
                      <thead>
                        <tr>
                          <th colSpan={2}>Statistics</th>
                          <th>P&gt;|t|</th>
                        </tr>
                      </thead>
                      <tbody>
                        {STAT_BOX_FIELDS.map((f, i) => (
                          <tr key={i}>
                            <th>{f.label}</th>
                            <td>
                              {this.renderFormattedField(f, latest_stock_stats)}
                            </td>
                            <td>
                              {this.renderFormattedField(
                                f,
                                latest_stock_stats,
                                "_p_gt_abs_t"
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                ""
              )}

              <div className="mt-2">
                {this.renderSpinner(stock_graph_loadingIndicator)}
                {!stock_graph_loadingIndicator && latest_stock_stats ? (
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
                        options={
                          s.name in stock_graph_stats_options
                            ? stock_graph_stats_options[s.name]
                            : stock_graph_options
                        }
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

            <div role="tabpanel" hidden={current_tab !== 1}>
              {this.renderSpinner(data_loadingIndicator)}
              {this.renderFieldsTable(
                StockDataService.stock_data_fields(),
                data,
                { skipTicker: true }
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
                stats,
                { skipTicker: true }
              )}
              {this.renderPaginator(
                stats_count,
                stats_page,
                stats_pageSize,
                this.handleStatsPageChange,
                this.handleStatsPageSizeChange
              )}
            </div>

            {comp_total ? (
              <div role="tabpanel" hidden={current_tab !== 3}>
                {this.renderSpinner(comp_loadingIndicator)}
                {this.renderFieldsTable(
                  StockDataService.stock_comp_fields(),
                  comp,
                  {
                    tableClassName: "selectable-items-table",
                    onRowClick: this.onStockComponentClick,
                  }
                )}
                {this.renderPaginator(
                  comp_count,
                  comp_page,
                  comp_pageSize,
                  this.handleComponentsPageChange,
                  this.handleComponentsPageSizeChange
                )}
              </div>
            ) : (
              ""
            )}

            <div role="tabpanel" hidden={current_tab !== (comp_total ? 4 : 3)}>
              {this.renderSpinner(parents_loadingIndicator)}
              {this.renderFieldsTable(
                StockDataService.stock_comp_fields(),
                parents,
                {
                  tableClassName: "selectable-items-table",
                  onRowClick: this.onStockParentClick,
                }
              )}
              {this.renderPaginator(
                parents_count,
                parents_page,
                parents_pageSize,
                this.handleParentsPageChange,
                this.handleParentsPageSizeChange
              )}
            </div>

            <p>{message}</p>
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

Stock.contextType = SeriesContext;

Stock.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      id: PropTypes.string
    }),
  }),
  history: PropTypes.any
}

export default withRouter(Stock);
