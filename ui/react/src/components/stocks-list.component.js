import PropTypes from 'prop-types';
import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";
import SeriesSettings, { SeriesContext } from "./series-settings.component";
import { CircularProgress, Pagination, IconButton } from "@mui/material";
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';

const FIELD_OPS = [
  { label: "=", value: "eq" },
  { label: ">", value: "gt" },
  { label: ">=", value: "gte" },
  { label: "<", value: "lt" },
  { label: "<=", value: "lte" },
  { label: "!=", value: "neq" },
  { label: "contains", value: "contains" },
];

const DEFAULT_PAGE_SIZE = 25;

class StocksList extends Component {
  constructor(props) {
    super(props);
    this.onChangeSearchValue = this.onChangeSearchValue.bind(this);
    this.retrieveStocks = this.retrieveStocks.bind(this);
    this.refreshList = this.refreshList.bind(this);
    this.refreshListFirstPage = this.refreshListFirstPage.bind(this);
    this.setActiveStock = this.setActiveStock.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
    this.handlePageSizeChange = this.handlePageSizeChange.bind(this);
    this.searchOnKeyUp = this.searchOnKeyUp.bind(this);
    this.handleSearchFieldChange = this.handleSearchFieldChange.bind(this);
    this.handleSearchOpChange = this.handleSearchOpChange.bind(this);
    this.addSearchField = this.addSearchField.bind(this);
    this.removeSearchField = this.removeSearchField.bind(this);
    this.syncCurrentUrl = this.syncCurrentUrl.bind(this);
    this.setSort = this.setSort.bind(this);

    this.state = {
      sortField: 'ticker',
      errorMessage: null,
      stocks: [],
      // default to ticker search only
      searchFields: [
        { ...StockDataService.fields()[0], value: "", op: "contains" },
      ],
      page: 1,
      count: 0,
      pageSize: DEFAULT_PAGE_SIZE,
      loadingIndicator: true,
    };

    this.pageSizes = [10, 25, 50, 100];
  }

  filterStringsToSearchFieldsArray(filters) {
    // format in URL <field>__<op>__<value>
    let res = { searchFields: [] };
    filters.forEach((f) => {
      let arr = f.split("__");
      if (arr.length !== 3) return;
      // find the field
      let nf = StockDataService.fields().find((el) => el.name === arr[0]);
      if (!nf) return;
      res.searchFields.push({ ...nf, op: arr[1], value: arr[2] });
    });
    return res;
  }

  componentDidMount() {
    this.prevContext = this.context;
    if (this.props.match.params.pageSize || this.props.match.params.page) {
      let update = {};
      if (this.props.match.params.pageSize) {
        update.pageSize = parseInt(this.props.match.params.pageSize);
      }
      if (this.props.match.params.page) {
        update.page = parseInt(this.props.match.params.page);
      }
      if (this.props.match.params.filters) {
        // format in URL <field>__<op>__<value>
        let filters = this.props.match.params.filters.split("/");
        let res = this.filterStringsToSearchFieldsArray(filters);
        if (res.searchFields.length) update.searchFields = res.searchFields;
      }
      console.log("componentDidMount:: Setting page params", update);
      this.setState(update, () => {
        this.retrieveStocks();
      });
    } else {
      this.retrieveStocks();
    }
  }

  componentDidUpdate(prevProps) {
    console.log(
      "componentDidUpdate:: prevProps / newProps",
      prevProps,
      this.props,
      this.context
    );
    let update = {};
    let changed = false;
    if (prevProps.match.params.pageSize !== this.props.match.params.pageSize) {
      let ps = parseInt(this.props.match.params.pageSize) || DEFAULT_PAGE_SIZE;
      if (ps !== this.state.pageSize) {
        update.pageSize = ps;
        changed = true;
      }
    }
    if (prevProps.match.params.page !== this.props.match.params.page) {
      let ps = parseInt(this.props.match.params.page) || 1;
      if (ps !== this.state.page) {
        update.page = ps;
        changed = true;
      }
    }
    if (this.prevContext.factorName != this.context.factorName || this.prevContext.frequency != this.context.frequency) {
      changed = true;
    }
    if (changed) {
      this.prevContext = this.context;
      console.log("componentDidUpdate:: update state", update);
      this.setState(update, () => {
        this.retrieveStocks();
      });
    }
  }

  searchOnKeyUp(event) {
    if (event.charCode === 13) {
      this.refreshListFirstPage();
    }
  }

  setSort(field) {
    let { sortField } = this.state;
    if (sortField === field) {
      sortField = '-' + field;
    } else {
      sortField = field;
    }
    this.setState({ sortField }, () => { this.retrieveStocks() })
  }

  renderSortHeader(label, field) {
    const { sortField } = this.state;
    let sortClass = '';
    if (sortField === field) {
      sortClass = 'sortAsc';
    } else if (sortField === '-'+field) {
      sortClass = 'sortDesc';
    }
    if (field) {
      return (<th scope="col" className={'sortableHeader ' + sortClass} onClick={()=>this.setSort(field)}>{label}<IconButton aria-label={label}><ArrowUpwardIcon/></IconButton></th>)
    } else {
      return (<th>{label}</th>)
    }
  }

  getRequestParams(searchFields, page, pageSize, factorName, frequency, sortField) {
    let params = {};

    if (searchFields && searchFields.length) {
      searchFields.forEach((e) => {
        params[`${e.name}__${e.op}`] = e.value;
      });
    }

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

    if (sortField) {
      params["sort"] = sortField;
    }

    console.log("getRequestParams:: params", params);
    return params;
  }

  retrieveStocks() {
    console.log("retrieveStocks:: state", this.state);
    console.log("retrieveStocks:: context", this.context);
    const { searchFields, page, pageSize, sortField } = this.state;
    const { frequency, factorName } = this.context;

    // reset error
    this.setState({ errorMessage: null });

    const params = this.getRequestParams(searchFields, page, pageSize, factorName, frequency, sortField);

    this.setState({ loadingIndicator: true });

    StockDataService.getAll(params)
      .then((response) => {
        const { items, totalPages } = response.data;

        this.setState({
          stocks: items,
          count: totalPages,
        });
        console.log(response.data);
        this.setState({ loadingIndicator: false });
      })
      .catch((e) => {
        console.log("Error from StockDataService.getAll:", e, e.response);
        let err = e;
        if (err.response && err.response.data && err.response.data.error) {
          err = err.response.data.error;
        } else if (err.message) {
          err = err.message;
        }
        this.setState({ errorMessage: err, loadingIndicator: false });
      });
  }

  refreshListFirstPage() {
    this.setState({ page: 1 }, () => {
      this.syncCurrentUrl();
      this.retrieveStocks();
    });
  }

  refreshList() {
    this.syncCurrentUrl();
    this.retrieveStocks();
  }

  setActiveStock(stock) {
    console.log("Changed active stock: ", stock);
    this.props.history.push(`/stocks/${stock.ticker}`);
  }

  onChangeSearchValue(event, index) {
    const val = event.target.value;
    this.setState((prevState) => ({
      searchFields: prevState.searchFields.map((el, j) =>
        j === index ? { ...el, value: val } : el
      ),
    }));
  }

  handleSearchFieldChange(event, index) {
    console.log("handleSearchFieldChange", index, event, event.target.value);
    // find the new selected field
    let nf = StockDataService.fields().find(
      (el) => el.name === event.target.value
    );
    this.setState((prevState) => ({
      searchFields: prevState.searchFields.map((el, j) =>
        j === index ? { ...el, name: nf.name, label: nf.label } : el
      ),
    }));
  }

  handleSearchOpChange(event, index) {
    console.log("handleSearchOpChange", index, event, event.target.value);
    this.setState((prevState) => ({
      searchFields: prevState.searchFields.map((el, j) =>
        j === index ? { ...el, op: event.target.value } : el
      ),
    }));
  }

  addSearchField(event, index) {
    console.log("addSearchField", index, event, event.target.value);
    // find the new selected field
    const nf = StockDataService.fields()[0];
    this.setState((prevState) => ({
      searchFields: prevState.searchFields.concat({
        ...nf,
        value: "",
        op: "contains",
      }),
    }));
  }

  removeSearchField(event, index) {
    console.log("removeSearchField", index, event, event.target.value);
    // don't remove all the fields.
    if (this.state.searchFields.length <= 1) return;
    this.setState(
      (prevState) => ({
        searchFields: prevState.searchFields.filter((_el, j) => index !== j),
      }),
      () => {
        this.refreshListFirstPage();
      }
    );
  }

  syncCurrentUrl() {
    let fs = [];
    this.state.searchFields.forEach((f) => {
      fs.push(`${f.name}__${f.op}__${f.value}`);
    });
    console.log("syncCurrentUrl:: with filters ", fs);
    this.props.history.push(
      `/stocks-list/${this.state.pageSize}/${this.state.page}/${fs.join("/")}`
    );
  }

  handlePageChange(event, value) {
    console.log("handlePageChange:: ", event, value);
    this.setState(
      {
        page: value,
      },
      () => {
        this.refreshList();
      }
    );
  }

  handlePageSizeChange(event) {
    console.log("handlePageSizeChange:: ", event);
    this.setState(
      {
        pageSize: event.target.value,
        page: 1,
      },
      () => {
        this.refreshList();
      }
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
    return (
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
    const { searchFields, stocks, page, count, pageSize, errorMessage } =
      this.state;

    return (
      <div className="list row">
        <SeriesSettings/>
        <div className="col-12">
          <div className="input-group mb-3">
            {searchFields.map((sf, i) => (
              <div className="input-group mb-3" key={i}>
                <select
                  className="form-select"
                  onChange={(e) => this.handleSearchFieldChange(e, i)}
                  value={sf.name}
                >
                  {StockDataService.fields().map((f) => (
                    <option key={f.name} value={f.name}>
                      {f.label}
                    </option>
                  ))}
                </select>
                <select
                  className="form-select"
                  onChange={(e) => this.handleSearchOpChange(e, i)}
                  value={sf.op}
                >
                  {FIELD_OPS.map((op) => (
                    <option key={op.value} value={op.value}>
                      {op.label}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  className="form-control"
                  placeholder={"Search by " + sf.label}
                  value={sf.value}
                  onChange={(e) => this.onChangeSearchValue(e, i)}
                  onKeyPress={this.searchOnKeyUp}
                />
                <button
                  className="btn btn-outline-secondary"
                  type="button"
                  onClick={(e) => this.removeSearchField(e, i)}
                >
                  -
                </button>
                <button
                  className="btn btn-outline-secondary"
                  type="button"
                  onClick={(e) => this.addSearchField(e, i)}
                >
                  +
                </button>
              </div>
            ))}
            <div className="input-group-append">
              <button
                className="btn btn-outline-secondary"
                type="button"
                disabled={this.state.loadingIndicator}
                onClick={this.refreshListFirstPage}
              >
                Search
              </button>
            </div>
          </div>
        </div>
        <div className="col-12">
          {this.renderSpinner(this.state.loadingIndicator)}
          {errorMessage ? (
            <div
              className="alert alert-danger d-flex align-items-center"
              role="alert"
            >
              <div>{errorMessage}</div>
            </div>
          ) : (
            ""
          )}
          <table className="table table-bordered selectable-items-table">
            <thead>
              <tr>
                {this.renderSortHeader('Stock', 'ticker')}
                {this.renderSortHeader('BMG', 'bmg')}
                {this.renderSortHeader('Market', 'mkt_rf')}
                {this.renderSortHeader('SMB', 'smb')}
                {this.renderSortHeader('HML', 'hml')}
                {this.renderSortHeader('WML', 'wml')}
                {this.renderSortHeader('R-sq', 'r_squared')}
              </tr>
            </thead>
            <tbody>
              {stocks &&
                stocks.map((item, index) => (
                  <tr
                    onClick={() => this.setActiveStock(item, index)}
                    key={index}
                  >
                    <td>
                      <b>{item.ticker}</b>: {item.name}
                    </td>
                    <td
                      data-pgtabs={item.bmg_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.bmg_p_gt_abs_t
                      )}
                    >
                      {item.bmg}
                    </td>
                    <td
                      data-pgtabs={item.mkt_rf_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.mkt_rf_p_gt_abs_t
                      )}
                    >
                      {item.mkt_rf}
                    </td>
                    <td
                      data-pgtabs={item.smb_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.smb_p_gt_abs_t
                      )}
                    >
                      {item.smb}
                    </td>
                    <td
                      data-pgtabs={item.hml_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.hml_p_gt_abs_t
                      )}
                    >
                      {item.hml}
                    </td>
                    <td
                      data-pgtabs={item.wml_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.wml_p_gt_abs_t
                      )}
                    >
                      {item.wml}
                    </td>
                    <td
                      data-pgtabs={item.r_squared_p_gt_abs_t}
                      className={StockDataService.getColoringClassForStat(
                        item.r_squared_p_gt_abs_t
                      )}
                    >
                      {item.r_squared}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {this.renderPaginator(
            count,
            page,
            pageSize,
            this.handlePageChange,
            this.handlePageSizeChange
          )}
        </div>
      </div>
    );
  }
}

StocksList.contextType = SeriesContext;

StocksList.propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      id: PropTypes.string,
      page: PropTypes.number,
      pageSize: PropTypes.number,
      filters: PropTypes.array,
    }),
  }),
  history: PropTypes.any
}

export default withRouter(StocksList);
