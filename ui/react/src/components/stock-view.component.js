import CircularProgress from "@mui/material/CircularProgress";
import Pagination from "@mui/material/Pagination";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import React, { Component } from "react";
import Linkify from "react-linkify";
import StockDataService from "../services/stock.service";

const componentDecorator = (href, text, key) => (
  <a href={href} key={key} target="_blank" rel="noreferrer">
    {text}
  </a>
);

const DEFAULT_PAGE_SIZE = 25;
const DEFAULT_TAB = 0;

export default class Stock extends Component {
  constructor(props) {
    super(props);
    this.getStock = this.getStock.bind(this);
    this.goBack = this.goBack.bind(this);
    this.handleTabChange = this.handleTabChange.bind(this);
    this.handleDataPageChange = this.handleDataPageChange.bind(this);
    this.handleDataPageSizeChange = this.handleDataPageSizeChange.bind(this);
    this.handleStatsPageChange = this.handleStatsPageChange.bind(this);
    this.handleStatsPageSizeChange = this.handleStatsPageSizeChange.bind(this);

    this.pageSizes = [10, 25, 50, 100];
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

  renderFormattedField(field, item) {
    return item[field.name] && field.fmtNumber
      ? parseInt(item[field.name]).toLocaleString()
      : item[field.name];
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
              Stock {current.ticker} {current.name}{" "}
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
                {StockDataService.fields()
                  .filter((f) => !f.searchOnly)
                  .map((f) => this.renderField(f, current))}
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
