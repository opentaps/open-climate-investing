import PropTypes from 'prop-types';
import React, { Component } from "react";
import { withRouter } from "react-router-dom";
import StockDataService from "../services/stock.service";


const DEFAULT_FACTOR_NAME = "DEFAULT";

class BmgAnalysis extends Component {
  constructor(props) {
    super(props);

    this.state = {
      factor_name: DEFAULT_FACTOR_NAME,
      factor_names: [],
      sectors: [],
      analysis: {}
    }
  }

  componentDidMount() {
    //this.retrieveFactorNames();
    this.retrieveAnalysis();
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
      const { data: res2 } = await StockDataService.getSectorsBmgAnalysis();
      console.log('sectors analysis? ', res2);
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
        analysis
      });
    } catch (err) {
      console.log(err);
    }
  }

  render() {
    const { analysis } = this.state;
    return (
      <div>
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
                {analysis.factors.map(f=><td key={`${s}_${f}`}>{analysis.values[s][f]} ({(100.0*analysis.values[s][f]/analysis.values[s]['_TOTAL_']).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}%)</td>)}
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
