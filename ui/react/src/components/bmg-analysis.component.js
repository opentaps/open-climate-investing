import PropTypes from 'prop-types';
import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";
import { FormControl, MenuItem, Select } from "@mui/material";


const DEFAULT_FACTOR_NAME = "DEFAULT";

class BmgAnalysis extends Component {
  constructor(props) {
    super(props);
    this.handleFactorNameChange = this.handleFactorNameChange.bind(this);
    this.onStockClick = this.onStockClick.bind(this);

    this.state = {
      factor_name: DEFAULT_FACTOR_NAME,
      factor_names: [],
      sectors: [],
      stocks: [],
      analysis: {}
    }
  }

  componentDidMount() {
    this.retrieveFactorNames();
    this.retrieveAnalysis();
  }

  handleFactorNameChange(event) {
    let value = event.target.value;
    console.log("handleFactorNameChange:: ", event, value);
    this.setState({
      factor_name: value,
    }, () => {
      this.retrieveAnalysis();
    });
  }

  async retrieveFactorNames() {
    try {
      const { data: factor_names } = await StockDataService.getFactorNames();
      this.setState({
        factor_names: factor_names.map((e) => e.factor_name),
      });
    } catch (err) {
      console.log(err);
    }
  }

  async retrieveAnalysis() {
    try {
      const { data: res1 } = await StockDataService.getBmgAnalysisBaseCount({t: 'XWD.TO'});
      console.log('count analysis? ', res1);
      const { data: res2 } = await StockDataService.getSectorsBmgAnalysis({f: this.state.factor_name});
      console.log('sectors analysis? ', res2);
      const { data: res3 } = await StockDataService.getStocksBmgAnalysis({f: this.state.factor_name});
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

  render() {
    const {
      analysis,
      stocks,
      factor_name,
      factor_names,
    } = this.state;

    return (
      <div>
        {factor_names && factor_names.length > 1 && (
          <div className="d-flex flex-row align-items-baseline mb-2">
            <b className="me-2">BMG Factor</b>
            <FormControl variant="standard">
              <Select
                value={factor_name}
                onChange={this.handleFactorNameChange}
              >
                {factor_names.map((fname) => (
                  <MenuItem key={fname} value={fname}>
                    {fname}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </div>
        )}
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
                {analysis.factors.map(f=><td key={`${s}_${f}`}>{analysis.values[s][f]||0} ({(100.0*(analysis.values[s][f]||0)/analysis.values[s]['_TOTAL_']).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}%)</td>)}
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
              </tr>
            </thead>
            <tbody>
            {stocks.map((s,index)=>(
              <tr key={s.ticker}>
                <th data-index={index} onClick={this.onStockClick}>{s.ticker}</th>
                <td data-index={index} onClick={this.onStockClick}>{s.sector}</td>
              </tr>
            ))}
            </tbody>
          </table>
        )}

      </div>
    )
  }
}


BmgAnalysis .propTypes = {
  match: PropTypes.shape({
    params: PropTypes.shape({
      id: PropTypes.string
    }),
  }),
  history: PropTypes.any
}

export default withRouter(BmgAnalysis );
