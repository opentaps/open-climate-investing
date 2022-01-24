import PropTypes from 'prop-types';
import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";
import SeriesSettings, { SeriesContext } from "./series-settings.component";
import { Pagination, IconButton } from "@mui/material";
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';

const DEFAULT_PAGE_SIZE = 25;

class BmgAnalysis extends Component {
  constructor(props) {
    super(props);
    this.onStockClick = this.onStockClick.bind(this);
    this.onSectorClick = this.onSectorClick.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);
    this.handlePageSizeChange = this.handlePageSizeChange.bind(this);
    this.setSort = this.setSort.bind(this);

    this.state = {
      sortField: 'sector',
      filter_sector: null,
      sectors: [],
      stocks: [],
      analysis: {},
      page: 1,
      count: 0,
      pageSize: DEFAULT_PAGE_SIZE
    }
    this.pageSizes = [10, 25, 50, 100];
  }

  componentDidMount() {
    this.prevContext = this.context;
    this.retrieveAnalysis();
  }

  componentDidUpdate() {
    let changed = false;
    if (this.prevContext.factorName != this.context.factorName || this.prevContext.frequency != this.context.frequency) {
      changed = true;
    }
    if (changed) {
      this.prevContext = this.context;
      this.retrieveAnalysis();
    }
  }

  handlePageChange(event, value) {
    console.log("handlePageChange:: ", event, value);
    this.setState(
      {
        page: value,
      },
      () => {
        this.retrieveAnalysis();
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
        this.retrieveAnalysis();
      }
    );
  }

  async retrieveAnalysis() {
    try {
      const { factorName, frequency } = this.context;
      const { page, pageSize, filter_sector, sortField } = this.state;
      const { data: res1 } = await StockDataService.getBmgAnalysisBaseCount({t: 'XWD.TO', frequency});
      console.log('count analysis? ', res1);
      let params = {f: factorName, frequency};
      const { data: res2 } = await StockDataService.getSectorsBmgAnalysis(params);
      console.log('sectors analysis? ', res2);
      if (filter_sector) params.sector = filter_sector;
      if (page) params["page"] = page - 1;
      if (pageSize) params["size"] = pageSize;
      if (sortField) params["sort"] = sortField;
      const { data: res3 } = await StockDataService.getStocksBmgAnalysis(params);
      const { items, totalPages } = res3;
      console.log('stocks analysis? ', res3);
      // process into a displayable data structure
      let analysis = res2.reduce((p,s) => {
        let k = p.values[s.sector] || {'_TOTAL_': 0};
        k[s.bmg_factor_name] = s.count;
        p.values[s.sector] = k;
        return p
      }, {
        factors: res2.map(s=>s.bmg_factor_name).filter((v,i,self)=>self.indexOf(v)===i),
        sectors: res1.map(s=>s.sector),
        values: res1.reduce((p,s)=>{p[s.sector]={'_TOTAL_':s.count};return p},{}),
        periods: items.reduce((p,s)=>{let t = parseInt(s.total); return t>p?t:p},0)
      });
      console.log('results analysis? ', analysis);
      this.setState({
        sectors: res1,
        analysis,
        stocks: items,
        count: totalPages
      });
    } catch (err) {
      console.log(err);
    }
  }

  onStockClick(e) {
    console.log("onStockClick", e);
    if (e && e.target && e.target.attributes["data-index"]) {
      let i = e.target.getAttribute("data-index");
      let item = this.state.stocks[i];
      console.log("onStockClick --> ", i, item);
      this.props.history.push(`/stocks/${item.ticker}`);
    }
  }

  onSectorClick(e) {
    if (e && e.target && e.target.attributes["data-sector"]) {
      let sector = e.target.getAttribute("data-sector");
      console.log("onSectorClick --> ", sector);
      if (this.state.filter_sector == sector) sector = null;
      this.setState({ filter_sector: sector }, () => this.retrieveAnalysis());
    }
  }

  fmtNum(v) {
    if (v === undefined || v === null) return '';
    let n = parseFloat(v);
    return n.toFixed(3);
  }

  fmtSectorCount(c,t) {
    if (!c) c = 0;
    return c + ' (' + (100.0*(c||0)/t).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) + '%)';
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

  setSort(field) {
    let { sortField } = this.state;
    if (sortField === field) {
      sortField = '-' + field;
    } else {
      sortField = field;
    }
    this.setState({ sortField }, () => { this.retrieveAnalysis() })
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
      return (<th className={'sortableHeader ' + sortClass} onClick={()=>this.setSort(field)}>{label}<IconButton aria-label={label}><ArrowUpwardIcon/></IconButton></th>)
    } else {
      return (<th>{label}</th>)
    }
  }

  render() {
    const {
      analysis,
      stocks,
      filter_sector,
      page,
      count,
      pageSize
    } = this.state;

    return (
      <div>
        <SeriesSettings/>
        <h3>Number of Significant Stocks by Industry</h3>
        {analysis && analysis.sectors && analysis.sectors.length ?(
          <table className='table table-bordered selectable-items-table'>
            <thead>
              <tr>
                <th/>
                <th>Total</th>
                {analysis.factors.map(f=><th key={f}>{f}</th>)}
              </tr>
            </thead>
            <tbody>
            {analysis.sectors.map((s)=>(
              <tr key={s} data-sector={s} onClick={this.onSectorClick} className={s==filter_sector?'selected':''}>
                <th data-sector={s}>{s}</th>
                <td data-sector={s}>{analysis.values[s]['_TOTAL_']}</td>
                {analysis.factors.map(f=><td key={`${s}_${f}`}>
                    {this.fmtSectorCount(analysis.values[s][f], analysis.values[s]['_TOTAL_'])}
                </td>)}
              </tr>
            ))}
            </tbody>
          </table>
        ) : ''}

        <h3>Significant Stocks</h3>
        {stocks && stocks.length ? (<>
          <p>Stocks with more than half of their periods of significant BMG factor are listed below.</p>
          <table className='table table-bordered selectable-items-table'>
            <thead className='datatable-header'>
              <tr>
                {this.renderSortHeader('Sector', 'sector')}
                {this.renderSortHeader('Stock', 'ticker')}
                {this.renderSortHeader('Name', 'name')}
                {this.renderSortHeader('#Periods', 'total')}
                {this.renderSortHeader('Avg BMG', 'avg_bmg')}
                {this.renderSortHeader('Min BMG t-stat', 'min_bmg_t_stat')}
                {this.renderSortHeader('Avg BMG t-stat', 'avg_bmg_t_stat')}
                {this.renderSortHeader('Max BMG t-stat', 'max_bmg_t_stat')}
              </tr>
            </thead>
            <tbody>
            {stocks.map((s,index)=>(
              <tr key={s.ticker}>
                <td data-index={index} onClick={this.onStockClick}>{s.sector}</td>
                <th data-index={index} onClick={this.onStockClick}>{s.ticker}</th>
                <td data-index={index} onClick={this.onStockClick}>{s.name}</td>
                <td data-index={index} onClick={this.onStockClick}>{s.significant} of {parseInt(s.significant)+parseInt(s.not_significant)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.avg_bmg)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.min_bmg_t_stat)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.avg_bmg_t_stat)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.max_bmg_t_stat)}</td>
              </tr>
            ))}
            </tbody>
          </table>
        </>) : 'None.'}
        {this.renderPaginator(
          count,
          page,
          pageSize,
          this.handlePageChange,
          this.handlePageSizeChange
        )}

      </div>
    )
  }
}

BmgAnalysis.contextType = SeriesContext;

BmgAnalysis .propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      id: PropTypes.string
    }),
  }),
  history: PropTypes.any
}

export default withRouter(BmgAnalysis);
