import PropTypes from 'prop-types';
import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";
import SeriesSettings, { SeriesContext } from "./series-settings.component";


class BmgAnalysis extends Component {
  constructor(props) {
    super(props);
    this.onStockClick = this.onStockClick.bind(this);

    this.state = {
      sectors: [],
      stocks: [],
      analysis: {}
    }
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

  async retrieveAnalysis() {
    try {
      const { factorName, frequency } = this.context;
      const { data: res1 } = await StockDataService.getBmgAnalysisBaseCount({t: 'XWD.TO', frequency});
      console.log('count analysis? ', res1);
      const { data: res2 } = await StockDataService.getSectorsBmgAnalysis({f: factorName, frequency});
      console.log('sectors analysis? ', res2);
      const { data: res3 } = await StockDataService.getStocksBmgAnalysis({f: factorName, frequency});
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
        values: res1.reduce((p,s)=>{p[s.sector]={'_TOTAL_':s.count};return p},{})
      });
      console.log('results analysis? ', analysis);
      this.setState({
        sectors: res1,
        analysis,
        stocks: res3
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

  fmtNum(v) {
    if (v === undefined || v === null) return '';
    let n = parseFloat(v);
    return n.toFixed(3);
  }

  fmtSectorCount(c,t) {
    if (!c) return 'None';
    return c + ' (' + (100.0*(c||0)/t).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) + '%)';
  }

  render() {
    const {
      analysis,
      stocks,
    } = this.state;

    return (
      <div>
        <SeriesSettings/>
        <h3>Number of Significant Stocks by Industry</h3>
        {analysis && analysis.sectors && analysis.sectors.length && (
          <table className='table table-bordered'>
            <thead>
              <tr>
                <th/>
                <th>Total</th>
                {analysis.factors.map(f=><th key={f}>{f}</th>)}
              </tr>
            </thead>
            <tbody>
            {analysis.sectors.map((s)=>(
              <tr key={s}>
                <th>{s}</th>
                <td>{analysis.values[s]['_TOTAL_']}</td>
                {analysis.factors.map(f=><td key={`${s}_${f}`}>
                    {this.fmtSectorCount(analysis.values[s][f], analysis.values[s]['_TOTAL_'])}
                </td>)}
              </tr>
            ))}
            </tbody>
          </table>
        )}

        <h3>Significant Stocks</h3>
        {stocks && stocks.length && (
          <table className='table table-bordered selectable-items-table'>
            <thead>
              <tr>
                <th>Stock</th>
                <th>Sector</th>
                <th>Name</th>
                <th>#Periods</th>
                <th>Avg BMG</th>
                <th>Min BMG t-stat</th>
                <th>Avg BMG t-stat</th>
                <th>Max BMG t-stat</th>
              </tr>
            </thead>
            <tbody>
            {stocks.map((s,index)=>(
              <tr key={s.ticker}>
                <th data-index={index} onClick={this.onStockClick}>{s.ticker}</th>
                <td data-index={index} onClick={this.onStockClick}>{s.sector}</td>
                <td data-index={index} onClick={this.onStockClick}>{s.name}</td>
                <td data-index={index} onClick={this.onStockClick}>{s.significant}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.avg_bmg)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.min_bmg_t_stat)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.avg_bmg_t_stat)}</td>
                <td data-index={index} onClick={this.onStockClick}>{this.fmtNum(s.max_bmg_t_stat)}</td>
              </tr>
            ))}
            </tbody>
          </table>
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
